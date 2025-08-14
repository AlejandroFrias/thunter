from subprocess import call
import tempfile
from typing import Annotated
import typer

from thunter.cli.ls import ls
from thunter import settings
from thunter.constants import Status
from thunter.settings import thunter_print
from thunter.task_hunter import TaskHunter
from thunter.parser import parse_task_display


app = typer.Typer()


@app.command()
def edit(
    ctx: typer.Context,
    task_identifier: Annotated[
        str | None,
        typer.Argument(
            help="Task ID or name to edit. Defaults to editing the CURRENT task.",
            show_default=False,
        ),
    ] = None,
):
    """Edit a task. Use with caution."""
    hunter = TaskHunter()
    if task_identifier and task_identifier.isdigit():
        task = hunter.get_task(task_identifier)
    else:
        task = hunter.get_task(
            task_identifier=task_identifier,
            statuses={Status.CURRENT, Status.IN_PROGRESS, Status.TODO},
        )

    if not task:
        thunter_print("Could not find task '" + (task_identifier or "CURRENT") + "'")
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tmp") as tf:
        tf.write(hunter.display_task(task.id))
        tf.flush()
        call(settings.EDITOR.split(" ") + [tf.name])

        with open(tf.name, mode="r") as tf:
            tf.seek(0)
            updated_task_to_parse = tf.read()

    parsed_task_data = parse_task_display(updated_task_to_parse)
    hunter.remove_task(task.id)
    new_updated_task = hunter.create_task(
        name=parsed_task_data.name,
        estimate=parsed_task_data.estimate,
        description=parsed_task_data.description,
        status=parsed_task_data.status,
        created_at=task.created_at,
    )
    for history_data in parsed_task_data.history:
        hunter.insert_history(
            taskid=new_updated_task.id,
            is_start=history_data.is_start,
            time=history_data.time,
        )

    ctx.invoke(ls, starts_with=new_updated_task.name, all=True)
