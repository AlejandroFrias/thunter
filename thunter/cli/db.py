from subprocess import call
import typer

from thunter.settings import DATABASE


app = typer.Typer()


@app.command()
def db():
    """Access the sqlite database directly. Tables: tasks, history

    sqlite3> SELECT * FROM tasks

    sqlite3> SELECT * FROM history WHERE taskid = 1 ORDER BY time DESC
    """
    call(["sqlite3", DATABASE])
