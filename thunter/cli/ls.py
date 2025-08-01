from collections import defaultdict
from typing import Annotated

import typer
from rich import box
from rich.table import Table

from thunter.constants import Status
from thunter.models.task_history_record import TaskHistoryRecord
from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter


app = typer.Typer()


@app.command("ls, list")
def ls(
    all: Annotated[
        bool | None,
        typer.Option(
            "--all",
            "-a",
            help="List all tasks (short for -citf)",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    open: Annotated[
        bool | None,
        typer.Option(
            "--open",
            "-o",
            help="List all open tasks (short for -cit)",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    started: Annotated[
        bool | None,
        typer.Option(
            "--started",
            "-s",
            help="List all started tasks (short for -ci)",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    current: Annotated[
        bool | None,
        typer.Option(
            "--current",
            "-c",
            help="List all Current tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    in_progress: Annotated[
        bool | None,
        typer.Option(
            "--in-progress",
            "-i",
            help="List all In Progress tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    todo: Annotated[
        bool | None,
        typer.Option(
            "--todo",
            "-t",
            help="List all TODO tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    finished: Annotated[
        bool | None,
        typer.Option(
            "--finished",
            "-f",
            help="List all Finished tasks",
            rich_help_panel="Status Filtering",
        ),
    ] = None,
    starts_with: Annotated[
        str | None,
        typer.Option(
            "--starts-with",
            "-S",
            help="Only tasks that start with STRING",
            rich_help_panel="Task Name Filtering",
        ),
    ] = None,
    contains: Annotated[
        str | None,
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
    thunter_print(table)
