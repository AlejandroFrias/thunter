from typing import Annotated
import typer

from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command()
def show(task_id: Annotated[str | None, typer.Argument()] = None):
    """Display task. Defaults to the currently active task if there is one."""
    hunter = TaskHunter()
    task = hunter.get_task(task_id)
    thunter_print(hunter.display_task(task.id))
