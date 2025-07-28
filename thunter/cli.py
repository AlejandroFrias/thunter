import shutil
import sys
import os
import tempfile
from collections import defaultdict
from subprocess import call
from io import StringIO
from typing import Optional
from typing_extensions import Annotated

import sqlite3
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from thunter import settings
from thunter.constants import (
    CURRENT_TASK_IDENTIFIER,
    ThunterError,
    ThunterCouldNotFindTaskError,
    Status,
)
from thunter.models.task_history_record import TaskHistoryRecord
from thunter.task_hunter import TaskHunter
from thunter.task_parser import parse_task

thunter_cli_app = typer.Typer(
    no_args_is_help=True,
    help="Thunter CLI - Task Hunter for tracking time spent on your to-do list.",
)

console = Console()
if settings.THUNTER_SILENT:
    console = Console(file=StringIO())


@thunter_cli_app.command()
def init():
    """Initialize thunter sqlite database.
    The database file name can be set with THUNTER_DATABASE_NAME, defaults to 'database.db'.
    The database file can be found in the THUNTER_DIRECTORY, defaults to ~/.thunter.
    """
    # check if db and thunter dir exist already exists
    if not settings.needs_init():
        prompt = (
            f"Are you sure you want to re-initialize and lose all tracking info? [yN]"
        )
        user_sure = input(prompt).lower() == "y"
        if not user_sure:
            console.print("Aborting re-initialization")
            return
        shutil.rmtree(settings.THUNTER_DIR)
    os.mkdir(settings.THUNTER_DIR)
    conn = sqlite3.connect(settings.DATABASE)
    conn.execute(
        "CREATE TABLE tasks(id INTEGER PRIMARY KEY, name TEXT, estimate INTEGER, description TEXT, status TEXT, last_modified INTEGER)"
    )
    conn.execute(
        "CREATE TABLE history(id INTEGER PRIMARY KEY, taskid INTEGER, is_start BOOLEAN, time INTEGER)"
    )
    conn.commit()
    conn.close()


# flake8: noqa
@thunter_cli_app.command()
def ls(
    all: Annotated[
        Optional[bool],
        typer.Option(
            "--all",
            "-a",
            help="List all tasks (short for -citf)",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    open: Annotated[
        Optional[bool],
        typer.Option(
            "--open",
            "-o",
            help="List all open tasks (short for -cit)",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    started: Annotated[
        Optional[bool],
        typer.Option(
            "--started",
            "-s",
            help="List all started tasks (short for -ci)",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    current: Annotated[
        Optional[bool],
        typer.Option(
            "--current",
            "-c",
            help="List all Current tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    in_progress: Annotated[
        Optional[bool],
        typer.Option(
            "--in-progress",
            "-i",
            help="List all In Progress tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    todo: Annotated[
        Optional[bool],
        typer.Option(
            "--todo",
            "-t",
            help="List all TODO tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    finished: Annotated[
        Optional[bool],
        typer.Option(
            "--finished",
            "-f",
            help="List all Finished tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    starts_with: Annotated[
        Optional[str],
        typer.Option(
            "--starts-with",
            "-S",
            help="Only tasks that start with STRING",
            rich_help_panel="Task Name Filtering",
        ),
    ] = None,
    contains: Annotated[
        Optional[str],
        typer.Option(
            "--contains",
            "-C",
            help="Only tasks that contain STRING",
            rich_help_panel="Task Name Filtering",
        ),
    ] = None,
):
    """List tasks. Defaults to listing all open tasks (CURRENT, IN_PROGRESS, TODO)."""
    statuses: set[Status] = set()
    if all:
        statuses.update(Status)
    if open:
        statuses.update([Status.CURRENT, Status.IN_PROGRESS, Status.TODO])
    if started:
        statuses.update([Status.CURRENT, Status.IN_PROGRESS])
    if current:
        statuses.add(Status.CURRENT)
    if in_progress:
        statuses.add(Status.IN_PROGRESS)
    if todo:
        statuses.add(Status.TODO)
    if finished:
        statuses.add(Status.FINISHED)
    if not statuses:
        statuses.update([Status.CURRENT, Status.IN_PROGRESS, Status.TODO])

    # Get the filtered and sorted list of tasks to display
    hunter = TaskHunter()
    tasks = hunter.get_tasks(
        statuses,
        starts_with=starts_with,
        contains=contains,
    )

    # Calculate progress from history
    history_records = hunter.get_history([task.id for task in tasks])
    taskid2history = defaultdict(list)
    for record in history_records:
        taskid2history[record.taskid].append(record)
    taskid2progress = defaultdict(int)
    for taskid, task_history in taskid2history.items():
        taskid2progress[taskid] = TaskHistoryRecord.calc_progress(task_history)

    # Pretty display in a table with colors
    table = Table(
        "ID",
        "NAME",
        "ESTIMATE",
        "PROGRESS",
        "STATUS",
        box=box.MINIMAL_HEAVY_HEAD,
    )
    for task in tasks:
        row = (
            str(task.id),
            task.name,
            task.estimate_display,
            TaskHistoryRecord.display_progress(taskid2progress[task.id]),
            task.status.value,
        )
        style = None
        if task.status == Status.CURRENT:
            style = "yellow"
        elif task.status == Status.IN_PROGRESS:
            style = "orange3"
        elif task.status == Status.FINISHED:
            style = "green"
        table.add_row(*row, style=style)
    console.print(table)


@thunter_cli_app.command()
def show(task_id: Annotated[Optional[str], typer.Argument()] = None):
    """Display task. Defaults to the currently active task if there is one."""
    hunter = TaskHunter()
    if task_id:
        task = hunter.get_task(task_id)
    else:
        task = hunter.get_current_task()
        if not task:
            console.print("No current task found.", style="red")
            return
    console.print(hunter.display_task(task.id))


@thunter_cli_app.command()
def create(
    task_id: Annotated[list[str], typer.Argument()],
    estimate: Annotated[
        Optional[int],
        typer.Option(
            "--estimate",
            "-e",
            help="Add estimate (in hours)",
            prompt="Estimate (hours)",
            min=1,
        ),
    ] = None,
    description: Annotated[
        Optional[str], typer.Option("--description", "-d", help="Add a description")
    ] = None,
):
    """Create a new task."""
    hunter = TaskHunter()
    new_task = hunter.create_task(
        " ".join(task_id),
        estimate=estimate,
        description=description,
    )
    show(task_id=str(new_task.id))


@thunter_cli_app.command()
def workon(
    task_id: Annotated[Optional[list[str]], typer.Argument()] = None,
    create: Annotated[
        Optional[bool],
        typer.Option(
            "--create",
            "-c",
            help="Create the task if it does not exist",
            rich_help_panel="Task Creation",
        ),
    ] = None,
    estimate_hours: Annotated[
        Optional[int],
        typer.Option(
            "--estimate",
            "-e",
            help="Add estimate (in hours) when creating a task",
            min=1,
            rich_help_panel="Task Creation",
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description",
            "-d",
            help="Add a description when creating a task",
            rich_help_panel="Task Creation",
        ),
    ] = None,
):
    """Start/continue working on an unfinished task."""
    hunter = TaskHunter()
    task_id_str = " ".join(task_id) if task_id else None
    try:
        task = hunter.get_task(
            task_id_str or CURRENT_TASK_IDENTIFIER,
            statuses=set([Status.CURRENT, Status.IN_PROGRESS, Status.TODO]),
        )
    except ThunterCouldNotFindTaskError:
        if task_id_str and create:
            task = hunter.create_task(
                name=task_id_str,
                estimate=estimate_hours,
                description=description,
            )
        else:
            raise

    hunter.workon_task(task.id)
    ls(open=True)


@thunter_cli_app.command()
def restart(task_id: Annotated[str, typer.Argument()]):
    """Restart a finished task (progress will continue from before)."""
    hunter = TaskHunter()
    task = hunter.get_task(task_id, statuses=set([Status.FINISHED]))
    if task:
        hunter.workon_task(task.id)
    ls(open=True)


@thunter_cli_app.command()
def stop():
    """Stop working on current task."""
    hunter = TaskHunter()
    stopped_task = hunter.stop_current_task()
    if not stopped_task:
        console.print("No current task to stop.", style="yellow")
    else:
        console.print(f"Stopped working on [yellow]{stopped_task.name}[/yellow]!")


@thunter_cli_app.command()
def finish(task_id: Annotated[Optional[str], typer.Argument()] = None):
    """Finish a task (defaults to finish current task)."""
    hunter = TaskHunter()
    task = None
    if task_id:
        task = hunter.get_task(task_id)
    else:
        task = hunter.stop_current_task()

    if not task:
        console.print("No task to finish.", style="yellow")
        return

    hunter.finish_task(task.id)
    console.print(f"Finished [green]{task.name}[/green]!")


@thunter_cli_app.command()
def estimate(
    estimate: Annotated[int, typer.Argument()],
    task_identifier: Annotated[
        Optional[str],
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
        console.print(
            "No current task found to estimate. Use --task-identifier / -t to specify a task.",
            style="red",
        )
        return

    hunter.estimate_task(task.id, estimate)
    task = hunter.get_task(task.id)
    console.print(
        f"[green]{task.name}[/green] estimated to take [yellow]{task.estimate_display}[/yellow]"
    )


@thunter_cli_app.command()
def edit(
    task_identifier: Annotated[
        Optional[str],
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
        console.print("Could not find task '" + (task_identifier or "CURRENT") + "'")
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp") as tf:
        tf.write(hunter.display_task(task.id))
        tf.flush()
        call(settings.EDITOR.split(" ") + [tf.name])

        with open(tf.name, mode="r") as tf:
            tf.seek(0)
            updated_task_to_parse = tf.read()

    parsed_task_data = parse_task(updated_task_to_parse)
    hunter.remove_task(task.id)
    new_updated_task = hunter.create_task(
        name=parsed_task_data["name"],
        estimate=parsed_task_data["estimate"],
        description=parsed_task_data["description"],
        status=parsed_task_data["status"],
    )
    for is_start, history_time in parsed_task_data["history"]:
        hunter.insert_history(
            taskid=new_updated_task.id, is_start=is_start, time=history_time
        )

    ls(starts_with=new_updated_task.name, all=True)


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
        console.print(f"Removed [red]{task.name}[/red]!")
    else:
        console.print(f"Didn't remove [yellow]{task.name}[/yellow].")


def main(silent: bool = False):
    """THunter - you task hunter, tracking time spent on your TODO list!"""
    try:
        thunter_cli_app()
    except KeyboardInterrupt:
        sys.exit(1)
    except ThunterError as thunter_error:
        if settings.DEBUG:
            console.print_exception(show_locals=True)
        console.print(str(thunter_error))
        sys.exit(thunter_error.exit_status)


if __name__ == "__main__":
    main()
