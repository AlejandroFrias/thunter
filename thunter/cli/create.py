from typing import Annotated
import typer

from thunter.cli.show import show
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command()
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
