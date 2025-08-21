import os
import shutil
from typing import Annotated

import typer

from thunter import settings
from thunter.db import Database
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
    db = Database()
    db.init_db()

    thunter_print("THunter initialized successfully!")
