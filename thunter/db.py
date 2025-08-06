from contextlib import contextmanager
import sqlite3

from thunter import settings
from thunter.constants import Status, TableName, ThunterNotInitializedError, now
from thunter.models.task import Task
from thunter.models.task_history_record import TaskHistoryRecord


class Database:
    """Base class for database interactions, supplying a context manager for
    database connections and handling initialization."""

    def __init__(self, database=None):
        if not database and settings.needs_init():
            raise ThunterNotInitializedError(
                "[red]Error[/red]: Run [bold]thunter init[/bold] to initialize task database"
            )
        if database:
            self.database = database
        else:
            self.database = settings.DATABASE

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.database)
        yield conn
        conn.commit()
        conn.close()

    def update_task_field(self, taskid: int, field: str, value: str | int) -> None:
        """Update a specific field of a task in the database."""
        sql = ("UPDATE {table} SET {field}=?, last_modified=? WHERE id=?").format(
            table=TableName.TASKS.value, field=field
        )
        sql_params = (value, now(), taskid)
        with self.connect() as conn:
            conn.execute(sql, sql_params)

    def select_from_task(
        self,
        where_clause: str | None = None,
        order_by: str | None = None,
        params: list[str] | None = None,
    ) -> list[Task]:
        return list(
            map(
                Task.from_db_record,
                self.select_from_table(TableName.TASKS, where_clause, order_by, params),
            )
        )

    def select_from_history(
        self,
        where_clause: str | None = None,
        order_by: str | None = None,
        params: list[str] | None = None,
    ) -> list[TaskHistoryRecord]:
        return list(
            map(
                TaskHistoryRecord.from_db_record,
                self.select_from_table(
                    TableName.HISTORY, where_clause, order_by, params
                ),
            )
        )

    def select_from_table(
        self,
        table: TableName,
        where_clause: str | None = None,
        order_by: str | None = None,
        params: list[str] | None = None,
    ):
        sql = "SELECT * FROM {table}".format(table=table.value)
        if where_clause:
            sql += " WHERE " + where_clause
        if order_by:
            sql += " ORDER BY " + order_by

        with self.connect() as conn:
            return conn.execute(sql, params or []).fetchall()

    def insert_task(
        self,
        name: str,
        estimate: int | None,
        description: str | None,
        status: Status,
        last_modified: int,
    ) -> int:
        """Insert a new task into the database and return its ID."""
        sql = (
            "INSERT INTO {table} "
            "(name,estimate,description,status,last_modified) "
            "VALUES (?,?,?,?,?)"
        ).format(table=TableName.TASKS.value)
        with self.connect() as conn:
            new_task_id = conn.execute(
                sql,
                (
                    name,
                    estimate,
                    description,
                    status.value,
                    last_modified,
                ),
            ).lastrowid
            if new_task_id is None:
                raise AssertionError(f"Could not insert task: {name}")
        return new_task_id

    def insert_history(self, taskid: int, is_start: bool, time: int) -> None:
        sql = ("INSERT INTO {table} (taskid,is_start,time) VALUES (?,?,?)").format(
            table=TableName.HISTORY.value
        )
        sql_params = (taskid, is_start, time)
        with self.connect() as conn:
            conn.execute(sql, sql_params)
