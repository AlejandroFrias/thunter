import typer

from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command()
def stop():
    """Stop working on current task."""
    hunter = TaskHunter()
    stopped_task = hunter.stop_current_task()
    if not stopped_task:
        thunter_print("No current task to stop.", style="yellow")
    else:
        thunter_print(f"Stopped working on [yellow]{stopped_task.name}[/yellow]!")
