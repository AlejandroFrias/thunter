from typing import Annotated
import typer

from thunter.constants import Status
from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command("f, finish")
def finish(task_id: Annotated[str | None, typer.Argument()] = None):
    """Finish a task (defaults to finish current task)."""
    hunter = TaskHunter()
    task = hunter.get_task(task_id)
    if task.status == Status.CURRENT:
        hunter.stop_current_task()

    hunter.finish_task(task.id)
    thunter_print(f"Finished [green]{task.name}[/green]!")
