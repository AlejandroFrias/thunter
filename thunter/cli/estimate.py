from typing import Annotated
import typer

from thunter.constants import ThunterCouldNotFindTaskError
from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command()
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
        f"[green]{task.name}[/green] estimated to take [yellow]{task.estimate_display}[/yellow]."
    )
