from typing import Annotated
import typer

from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command()
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
