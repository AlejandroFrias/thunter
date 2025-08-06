import typer
from IPython import embed

from thunter.task_analyzer import TaskAnalyzer

app = typer.Typer()


@app.command()
def analyze():
    """Create a new task."""
    analyzer = TaskAnalyzer()
    df = analyzer.fetch_data_df()

    # Convert start times to negative
    # df.loc[df["is_start"], 'time'] *= -1
    # sum up the time for each task
    # actual_time = df.groupby("id", sort=False)["time"].sum()
    embed()
