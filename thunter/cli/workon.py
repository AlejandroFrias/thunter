from typing import Annotated
import typer

from thunter.cli.ls import ls
from thunter.constants import Status, ThunterCouldNotFindTaskError
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command("w, workon")
def workon(
    ctx: typer.Context,
    task_id: Annotated[list[str] | None, typer.Argument()] = None,
    create: Annotated[
        bool | None,
        typer.Option(
            "--create",
            "-c",
            help="Create the task if it does not exist",
            rich_help_panel="Task Creation",
        ),
    ] = None,
    estimate_hours: Annotated[
        int | None,
        typer.Option(
            "--estimate",
            "-e",
            help="Add estimate (in hours) when creating a task",
            min=1,
            rich_help_panel="Task Creation",
        ),
    ] = None,
    description: Annotated[
        str | None,
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
            task_identifier=task_id_str,
            statuses=set([Status.CURRENT, Status.IN_PROGRESS, Status.TODO]),
            exact_match=True,
        )
    except ThunterCouldNotFindTaskError:
        if task_id_str:
            if create:
                task = hunter.create_task(
                    name=task_id_str,
                    estimate=get_estimate(estimate_hours),
                    description=description,
                )
            else:
                # try to find task with a partial match
                task = hunter.get_task(
                    task_identifier=task_id_str,
                    statuses=set([Status.CURRENT, Status.IN_PROGRESS, Status.TODO]),
                    exact_match=False,
                )
        else:
            raise

    hunter.workon_task(task.id)
    ctx.invoke(ls, current=True)


def get_estimate(estimate_hours: int | None) -> int:
    """Prompt user for an estimate if one was not given yet."""
    while estimate_hours is None or estimate_hours < 1:
        estimate_hours = typer.prompt("Estimate (hours)", type=int)
        if not estimate_hours or isinstance(estimate_hours, int) and estimate_hours < 1:
            typer.echo("Estimate must be at least 1 hour.")
    return estimate_hours
