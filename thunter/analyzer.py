import pandas as pd

from thunter.constants import TableName
from thunter.db import Database


class TaskAnalyzer(Database):
    """Collection data analysis operations for tasks and history."""

    def fetch_data_df(self) -> pd.DataFrame:
        """Fetch the data as a DataFrame for use by analysis tools."""
        with self.connect() as con:
            df = pd.read_sql(
                (
                    f"SELECT tasks.id, tasks.estimate, tasks.name, history.is_start, history.time FROM {TableName.TASKS.value} "
                    f"INNER JOIN {TableName.HISTORY.value} ON {TableName.TASKS.value}.id = {TableName.HISTORY.value}.taskid "
                    f"ORDER BY history.time ASC"
                ),
                con=con,
                dtype={
                    "estimate": pd.Int32Dtype(),
                    "is_start": pd.BooleanDtype(),
                    "name": pd.StringDtype(),
                    "time": pd.Int64Dtype(),
                },
            )

        return df

    def fetch_tasks_df(self) -> pd.DataFrame:
        """Fetch the tasks as a DataFrame."""
        with self.connect() as con:
            df = pd.read_sql(
                f"SELECT id, estimate, name, status, created_at FROM {TableName.TASKS.value}",
                con=con,
                parse_dates={"created_at": "s"},
            )

        return df

    def fetch_history_df(self) -> pd.DataFrame:
        """Fetch the tasks as a DataFrame."""
        with self.connect() as con:
            df = pd.read_sql(
                f"SELECT id, taskid, is_start, time FROM {TableName.HISTORY.value} ORDER BY taskid, time ASC",
                con=con,
                dtype={"is_start": bool},
            )

        return df
