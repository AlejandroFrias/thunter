from contextlib import contextmanager

import sqlite3

from thunter import settings
from thunter.constants import Status, TableName
from thunter.models.task import Task
from thunter.models.task_history_record import TaskHistoryRecord
from thunter.time import now_sec


class Database:
    """Base class for database interactions, supplying a context manager for
    database connections and handling initialization."""

    def __init__(self, database=None):
        self.database = database or settings.DATABASE

    def init_db(self):
        """Setup the database and tables. Does nothing if the database is already initialized."""
        with self.connect() as con:
            con.execute(
                f"CREATE TABLE IF NOT EXISTS {TableName.TASKS.value} ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT NOT NULL, "
                "estimate INTEGER, "
                "description TEXT, "
                "status TEXT NOT NULL, "
                "last_modified_at INTEGER NOT NULL DEFAULT (CAST(strftime('%s', current_timestamp) AS integer)), "
                "created_at INTEGER NOT NULL DEFAULT (CAST(strftime('%s', current_timestamp) AS integer))"
                ")"
            )
            con.execute(
                f"CREATE TABLE IF NOT EXISTS {TableName.HISTORY.value} ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "taskid INTEGER NOT NULL,"
                "is_start BOOLEAN NOT NULL,"
                "time INTEGER NOT NULL DEFAULT (CAST(strftime('%s', current_timestamp) AS integer)),"
                f"FOREIGN KEY (taskid) REFERENCES {TableName.TASKS.value}(id)"
                ")"
            )
            con.execute(
                "CREATE TRIGGER IF NOT EXISTS last_modified_task_trigger "
                f"AFTER UPDATE ON {TableName.TASKS.value} "
                "BEGIN"
                f"  UPDATE {TableName.TASKS.value} SET last_modified_at = "
                "  (CAST(strftime('%s', current_timestamp) AS integer)) "
                "  WHERE id = NEW.id;"
                "END;"
            )

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.database)
        yield conn
        conn.commit()
        conn.close()

    def update_task_field(self, taskid: int, field: str, value: str | int) -> None:
        """Update a specific field of a task in the database."""
        sql = ("UPDATE {table} SET {field}=?, last_modified_at=? WHERE id=?").format(
            table=TableName.TASKS.value, field=field
        )
        sql_params = (value, now_sec(), taskid)
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
        created_at: int | None = None,
    ) -> int:
        """Insert a new task into the database and return its ID."""
        if created_at is None:
            sql = (
                f"INSERT INTO {TableName.TASKS.value} "
                "(name,estimate,description,status) "
                "VALUES (?,?,?,?)"
            )
            sql_params = (
                name,
                estimate,
                description,
                status.value,
            )
        else:
            sql = (
                f"INSERT INTO {TableName.TASKS.value} "
                "(name,estimate,description,status,created_at) "
                "VALUES (?,?,?,?,?)"
            )
            sql_params = (
                name,
                estimate,
                description,
                status.value,
                created_at,
            )
        with self.connect() as conn:
            new_task_id = conn.execute(sql, sql_params).lastrowid
            if new_task_id is None:
                raise AssertionError(f"Could not insert task: {name}")
        return new_task_id

    def insert_history(
        self, taskid: int, is_start: bool, time: int | None = None
    ) -> None:
        if time is None:
            sql = (
                f"INSERT INTO {TableName.HISTORY.value} (taskid,is_start) VALUES (?,?)"
            )
            sql_params = (taskid, is_start)
        else:
            sql = ("INSERT INTO {table} (taskid,is_start,time) VALUES (?,?,?)").format(
                table=TableName.HISTORY.value
            )
            sql_params = (taskid, is_start, time)

        with self.connect() as conn:
            conn.execute(sql, sql_params)
