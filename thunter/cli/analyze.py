import typer
from IPython import embed

from thunter.constants import Status
from thunter.analyzer import TaskAnalyzer

app = typer.Typer()


@app.command()
def analyze():
    """Create a new task."""
    analyzer = TaskAnalyzer()
    df = analyzer.fetch_data_df()  # noqa: F841
    tasks_df = analyzer.fetch_tasks_df()
    history_df = analyzer.fetch_history_df()

    # TODO: merge dataframes and filter to just FINISHED tasks
    # Convert start times to negative
    history_df.loc[history_df["is_start"], "time"] *= -1
    # sum up the time for each task
    actual_time = history_df.groupby("taskid", sort=False)["time"].sum()
    finished_tasks = tasks_df[tasks_df["status"] == Status.FINISHED.value]
    comparison_df = finished_tasks.merge(actual_time, left_on="id", right_on="taskid")  # noqa: F841

    # TODO: time series plot of estimate vs actual

    embed()
