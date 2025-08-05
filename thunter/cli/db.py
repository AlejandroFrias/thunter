from subprocess import call
import typer

from thunter.settings import DATABASE


app = typer.Typer()


@app.command()
def db(
    ctx: typer.Context,
):
    """Access the sqlite database directly"""

    call(["sqlite3", DATABASE])
