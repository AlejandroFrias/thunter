from typing import Annotated
import typer

from thunter.cli.ls import ls
from thunter.constants import Status
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command()
def restart(ctx: typer.Context, task_id: Annotated[str, typer.Argument()]):
    """Restart a finished task (progress will continue from before)."""
    hunter = TaskHunter()
    task = hunter.get_task(task_id, statuses=set([Status.FINISHED]))
    hunter.workon_task(task.id)
    ctx.invoke(ls, current=True)
