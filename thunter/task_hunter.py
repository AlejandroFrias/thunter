from contextlib import contextmanager
import sqlite3
import time
from datetime import datetime
from thunter import settings
from thunter.constants import (
    Status,
    TableName,
    ThunterCouldNotFindTaskError,
    ThunterFoundMultipleTasksError,
    ThunterNotInitializedError,
)
from thunter.models import Task, TaskHistoryRecord, TaskIdentifier
from thunter.task_parser import display_task


def now():
    return int(time.mktime(datetime.now().timetuple()))


class TaskHunter:
    """The tasks manager class for interacting with tasks and their time tracking history."""

    def __init__(self, database=None):
        if not database and settings.needs_init():
            raise ThunterNotInitializedError(
                "[red]Error[/red]: Run [bold]thunter init[/bold] to initialize task database"
            )
        if database:
            self.database = database
        else:
            self.database = settings.DATABASE

    def get_task(
        self,
        task_identifier: TaskIdentifier | None = None,
        statuses: set[Status] | None = None,
    ) -> Task:
        """Fetch a task from the db by its identifier (name or id).
        Defaults to returning the current task if no identifier is given.

        Optionally filter by statuses in the search.

        Raises:
            ThunterCouldNotFindTaskError: If no task is found.
            ThunterFoundMultipleTasksError: If multiple tasks match the identifier.

        Returns:
            Task: The task object that matches the identifier.
        """
        if not task_identifier:
            current_task = self.get_current_task()
            if not current_task:
                raise ThunterCouldNotFindTaskError("No Current task found.")
            return current_task

        params: list[str] = []
        if isinstance(task_identifier, int) or task_identifier.isdigit():
            where_clause = "id=?"
            params = [str(task_identifier)]
        else:
            where_clause = "name LIKE ?"
            params = [task_identifier + "%"]

        if statuses:
            where_clause += " AND status IN (" + ",".join(len(statuses) * "?") + ")"
            params.extend(map(lambda s: s.value, statuses))

        order_by: str = "last_modified DESC"
        tasks = self.select_from_task(
            where_clause=where_clause, order_by=order_by, params=params
        )

        if len(tasks) == 0:
            raise ThunterCouldNotFindTaskError(
                f"Could not find task for identifier: {task_identifier}"
            )
        elif len(tasks) > 1:
            raise ThunterFoundMultipleTasksError(
                f"Found multiple tasks for identifier: {task_identifier}"
            )

        return tasks[0]

    def display_task(self, taskid: int):
        """Return a string representation of the task and its history.

        This representation is able to be parsed and is used by the edit command."""
        task = self.get_task(taskid)
        task_history = self.get_history([taskid])
        return display_task(task=task, task_history=task_history)

    def create_task(
        self,
        name: str,
        estimate: int | None = None,
        description: str | None = None,
        status: Status = Status.TODO,
    ) -> Task:
        """Create a new task in the database and return it."""
        new_task_id = self.insert_task(
            name, estimate, description, status, last_modified=now()
        )
        return self.get_task(new_task_id)

    def get_tasks(
        self,
        statuses: set[Status] | None = None,
        starts_with: str | None = None,
        contains: str | None = None,
    ) -> list[Task]:
        """Fetch a list tasks from the database with optional filters."""
        where_clause_param_pairs = []
        if starts_with:
            where_clause_param_pairs.append(("name LIKE ?", (starts_with + "%",)))
        if contains:
            where_clause_param_pairs.append(("name LIKE ?", ("%" + contains + "%",)))
        if statuses:
            where_clause_param_pairs.append(
                (
                    "status IN (" + ",".join(len(statuses) * "?") + ")",
                    map(lambda s: s.value, statuses),
                )
            )
        if where_clause_param_pairs:
            where_clauses, where_params = zip(*where_clause_param_pairs)
            where_clause = " AND ".join(where_clauses)
            params = [param for params in where_params for param in params]
        else:
            where_clause = None
            params = None

        tasks = self.select_from_task(where_clause=where_clause, params=params)
        return sorted(tasks)

    def get_history(self, taskids: list[int]) -> list[TaskHistoryRecord]:
        """Fetch the history records for a given task or list of tasks."""
        assert all(map(lambda taskid: isinstance(taskid, int), taskids))

        where_clause = "taskid IN (" + ",".join(len(taskids) * "?") + ")"
        history = self.select_from_history(
            where_clause=where_clause, params=list(map(str, taskids))
        )
        return sorted(history)

    def get_current_task(self) -> Task | None:
        """Fetch the current task from the database.

        There should only ever be one current task actively being worked on at
        a time.
        """
        current_tasks = self.select_from_task(
            where_clause="status IN (?)",
            params=[Status.CURRENT.value],
        )
        if len(current_tasks) == 0:
            return None
        elif len(current_tasks) > 1:
            raise AssertionError("More than one current task? How!?")

        return current_tasks[0]

    def workon_task(self, task_identifier: TaskIdentifier) -> None:
        """Start working on a task by its identifier (name or id).

        Stops tracking time spent on the current task if there is one, changing its status
        to IN_PROGRESS, and starts tracking time on the new task, changing its status to CURRENT.

        No-op if the identifier matches the current task.
        """
        task = self.get_task(task_identifier)
        current_task = self.get_current_task()
        if current_task:
            if current_task.id == task.id:
                return
            self.insert_history(taskid=current_task.id, is_start=False, time=now())
            self.update_task_field(current_task.id, "status", Status.IN_PROGRESS.value)
        self.insert_history(taskid=task.id, is_start=True, time=now())
        self.update_task_field(task.id, "status", Status.CURRENT.value)

    def stop_current_task(self) -> Task | None:
        """Stop tracking the current task and change its status to IN_PROGRESS."""
        current_task = self.get_current_task()
        if not current_task:
            return
        self.insert_history(taskid=current_task.id, is_start=False, time=now())
        self.update_task_field(current_task.id, "status", Status.IN_PROGRESS.value)
        return self.get_task(current_task.id)

    def finish_task(self, taskid: int) -> None:
        """Mark a task as finished and update its status."""
        task = self.get_task(taskid)
        if task.status == Status.CURRENT:
            self.insert_history(taskid=task.id, is_start=False, time=now())

        if task.status != Status.FINISHED:
            self.update_task_field(
                taskid=task.id, field="status", value=Status.FINISHED.value
            )

    def estimate_task(self, taskid: int, estimate: int) -> None:
        """(Re)set the estimate for a task."""
        self.update_task_field(taskid, "estimate", estimate)

    def remove_task(self, taskid: int) -> None:
        """Permanently delete a task and its history from the database."""
        delete_task_sql = "DELETE from {table} WHERE id=?".format(
            table=TableName.TASKS.value
        )
        delete_history_sql = "DELETE from {table} WHERE taskid=?".format(
            table=TableName.HISTORY.value
        )
        self.execute(delete_task_sql, (taskid,))
        self.execute(delete_history_sql, (taskid,))

    def update_task_field(self, taskid: int, field: str, value: str | int) -> None:
        """Update a specific field of a task in the database."""
        sql = ("UPDATE {table} SET {field}=?, last_modified=? " "WHERE id=?").format(
            table=TableName.TASKS.value, field=field
        )
        self.execute(sql, (value, now(), taskid))

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
            if new_task_id == None:
                raise AssertionError(f"Could not insert task: {name}")
        return new_task_id

    def insert_history(self, taskid: int, is_start: bool, time: int) -> None:
        sql = ("INSERT INTO {table} (taskid,is_start,time) VALUES " "(?,?,?)").format(
            table=TableName.HISTORY.value
        )
        self.execute(sql, (taskid, is_start, time))

    def execute(self, sql, sql_params=None):
        if sql_params is None:
            sql_params = []
        with self.connect() as conn:
            rows = conn.execute(sql, sql_params).fetchall()
        return rows

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.database)
        yield conn
        conn.commit()
        conn.close()
