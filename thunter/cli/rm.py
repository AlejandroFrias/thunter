from typing import Annotated
import typer

from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command("rm, remove")
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
