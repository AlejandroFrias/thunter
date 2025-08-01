import re
import sys
import tempfile
from subprocess import call
from typing_extensions import Annotated

import typer.core
from rich.console import Console

from thunter.settings import (
    thunter_print,
    print_config,
    needs_init,
    THUNTER_SILENT,
    DEBUG,
    EDITOR,
)
from thunter.cli.init import app as init_app, init
from thunter.cli.ls import app as ls_app, ls
from thunter.cli.show import app as show_app, show
from thunter.cli.workon import app as workon_app
from thunter.constants import (
    ThunterError,
    ThunterCouldNotFindTaskError,
    Status,
)
from thunter.task_hunter import TaskHunter
from thunter.task_parser import parse_task_display


class AliasGroup(typer.core.TyperGroup):
    """Custom override of TyperGroup to support command aliases.

    Watch this issue for possible native support in Typer for aliases:
    https://github.com/fastapi/typer/issues/1242
    """

    _CMD_SPLIT_P = re.compile(r" ?[,|] ?")

    def get_command(self, ctx, cmd_name):
        cmd_name = self._group_cmd_name(cmd_name)
        return super().get_command(ctx, cmd_name)

    def _group_cmd_name(self, default_name):
        for cmd in self.commands.values():
            name = cmd.name
            if name and default_name in self._CMD_SPLIT_P.split(name):
                return name
        return default_name


thunter_cli_app = typer.Typer(
    name="thunter",
    no_args_is_help=True,
    cls=AliasGroup,
)
thunter_cli_app.add_typer(init_app)
thunter_cli_app.add_typer(ls_app)
thunter_cli_app.add_typer(show_app)
thunter_cli_app.add_typer(workon_app)


@thunter_cli_app.callback()
def main_callback(
    ctx: typer.Context,
    silent: Annotated[
        bool,
        typer.Option(
            "--silent",
            "--quite",
            "-s",
            help="Run thunter in silent mode, no output to console.",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help="Run thunter in debug mode, printing out full exceptions and traces.",
        ),
    ] = False,
):
    """THunter - your task hunter, tracking time spent on your TODO list!"""
    print_config["silent"] = silent or THUNTER_SILENT
    print_config["debug"] = debug or DEBUG
    if ctx.invoked_subcommand != "init" and needs_init():
        ctx.invoke(init)


@thunter_cli_app.command()
def create(
    ctx: typer.Context,
    task_id: Annotated[list[str], typer.Argument()],
    estimate: Annotated[
        int | None,
        typer.Option(
            "--estimate",
            "-e",
            help="Add estimate (in hours)",
            prompt="Estimate (hours)",
            min=1,
        ),
    ] = None,
    description: Annotated[
        str | None, typer.Option("--description", "-d", help="Add a description")
    ] = None,
):
    """Create a new task."""
    hunter = TaskHunter()
    new_task = hunter.create_task(
        name=" ".join(task_id),
        estimate=estimate,
        description=description,
    )
    ctx.invoke(show, task_id=str(new_task.id))


@thunter_cli_app.command()
def restart(ctx: typer.Context, task_id: Annotated[str, typer.Argument()]):
    """Restart a finished task (progress will continue from before)."""
    hunter = TaskHunter()
    task = hunter.get_task(task_id, statuses=set([Status.FINISHED]))
    if task:
        hunter.workon_task(task.id)
    ctx.invoke(ls, open=True)


@thunter_cli_app.command()
def stop():
    """Stop working on current task."""
    hunter = TaskHunter()
    stopped_task = hunter.stop_current_task()
    if not stopped_task:
        thunter_print("No current task to stop.", style="yellow")
    else:
        thunter_print(f"Stopped working on [yellow]{stopped_task.name}[/yellow]!")


@thunter_cli_app.command()
def finish(task_id: Annotated[str | None, typer.Argument()] = None):
    """Finish a task (defaults to finish current task)."""
    hunter = TaskHunter()
    task = None
    if task_id:
        task = hunter.get_task(task_id)
    else:
        task = hunter.stop_current_task()

    if not task:
        thunter_print("No task to finish.", style="yellow")
        return

    hunter.finish_task(task.id)
    thunter_print(f"Finished [green]{task.name}[/green]!")


@thunter_cli_app.command()
def estimate(
    estimate: Annotated[int, typer.Argument()],
    task_identifier: Annotated[
        str | None,
        typer.Option(
            "--task-identifier",
            "-t",
            help="Estimate task by ID or name, instead of current task",
            show_default=False,
        ),
    ] = None,
):
    """Estimate how long a task will take."""
    hunter = TaskHunter()
    if task_identifier:
        task = hunter.get_task(task_identifier)
    else:
        task = hunter.get_current_task()

    if not task:
        raise ThunterCouldNotFindTaskError(
            "No current task found to estimate. Use --task-identifier / -t to specify a task."
        )

    hunter.estimate_task(task.id, estimate)
    task = hunter.get_task(task.id)
    thunter_print(
        f"[green]{task.name}[/green] estimated to take [yellow]{task.estimate_display}[/yellow]"
    )


@thunter_cli_app.command()
def edit(
    ctx: typer.Context,
    task_identifier: Annotated[
        str | None,
        typer.Argument(
            help="Task ID or name to edit. Defaults to editing the CURRENT task.",
            show_default=False,
        ),
    ] = None,
):
    """Edit a task. Use with caution."""
    hunter = TaskHunter()
    if task_identifier:
        task = hunter.get_task(task_identifier)
    else:
        task = hunter.get_current_task()

    if not task:
        thunter_print("Could not find task '" + (task_identifier or "CURRENT") + "'")
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp") as tf:
        tf.write(hunter.display_task(task.id))
        tf.flush()
        call(EDITOR.split(" ") + [tf.name])

        with open(tf.name, mode="r") as tf:
            tf.seek(0)
            updated_task_to_parse = tf.read()

    parsed_task_data = parse_task_display(updated_task_to_parse)
    hunter.remove_task(task.id)
    new_updated_task = hunter.create_task(
        name=parsed_task_data.name,
        estimate=parsed_task_data.estimate,
        description=parsed_task_data.description,
        status=parsed_task_data.status,
    )
    for history_data in parsed_task_data.history:
        hunter.insert_history(
            taskid=new_updated_task.id,
            is_start=history_data.is_start,
            time=history_data.time,
        )

    ctx.invoke(ls, starts_with=new_updated_task.name, all=True)


@thunter_cli_app.command()
def rm(
    task_id: Annotated[
        list[str], typer.Argument(help="ID or name of task to be removed.")
    ],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="No confirmation prompt")
    ] = False,
):
    """Remove/delete a task."""
    hunter = TaskHunter()
    task_identifier = " ".join(task_id)
    task = hunter.get_task(task_identifier)

    if force:
        user_is_sure = True
    else:
        prompt = (
            f"Are you sure you want to permanently delete [red]{task.name}[/red]!? [yN]"
        )
        user_is_sure = input(prompt).lower() == "y"

    if user_is_sure:
        hunter.remove_task(task.id)
        thunter_print(f"Removed [red]{task.name}[/red]!")
    else:
        thunter_print(f"Didn't remove [yellow]{task.name}[/yellow].")


def main(silent: bool = False):
    """THunter - you task hunter, tracking time spent on your TODO list!"""
    try:
        thunter_cli_app()
    except KeyboardInterrupt:
        sys.exit(1)
    except ThunterError as thunter_error:
        console = Console()
        if print_config["debug"]:
            console.print_exception(show_locals=True)
        console.print(str(thunter_error))
        sys.exit(thunter_error.exit_status)


if __name__ == "__main__":
    main()
