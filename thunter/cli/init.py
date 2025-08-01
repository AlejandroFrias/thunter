import os
import shutil
import sqlite3
from typing import Annotated

import typer

from thunter.constants import TableName
from thunter import settings
from thunter.settings import thunter_print, needs_init

app = typer.Typer()


@app.command()
def init(
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation prompt")
    ] = False,
):
    """Initialize thunter sqlite database.

    The database file name can be set with THUNTER_DATABASE_NAME, defaults to 'database.db'.
    The database file can be found in the THUNTER_DIRECTORY, defaults to ~/.thunter.
    """
    thunter_print("Initializing THunter...")
    if not needs_init():
        prompt = "WARNING: Are you sure you want to re-initialize? You will lose all tasks and tracking info [yN]"
        user_sure = force or input(prompt).lower() == "y"
        if not user_sure:
            thunter_print("Aborting re-initialization")
            raise typer.Exit()
        thunter_print(f"Deleting THunter directory: {settings.THUNTER_DIR}")
        shutil.rmtree(settings.THUNTER_DIR)
    if not os.path.exists(settings.THUNTER_DIR):
        thunter_print(f"Creating THunter directory: {settings.THUNTER_DIR}")
        os.mkdir(settings.THUNTER_DIR)
    thunter_print(f"Creating sqlite database {settings.DATABASE}")
    conn = sqlite3.connect(settings.DATABASE)

    thunter_print("Creating tables")
    create_tasks_table_sql = f"CREATE TABLE {TableName.TASKS.value}(id INTEGER PRIMARY KEY, name TEXT, estimate INTEGER, description TEXT, status TEXT, last_modified INTEGER)"
    thunter_print(create_tasks_table_sql)
    conn.execute(create_tasks_table_sql)
    create_history_table_sql = f"CREATE TABLE {TableName.HISTORY.value}(id INTEGER PRIMARY KEY, taskid INTEGER, is_start BOOLEAN, time INTEGER)"
    thunter_print(create_history_table_sql)
    conn.execute(create_history_table_sql)

    conn.commit()
    conn.close()
    thunter_print("THunter initialized successfully!")
