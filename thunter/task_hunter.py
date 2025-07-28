from contextlib import contextmanager
import sqlite3
import time
from datetime import datetime
from typing import Optional, Union
from thunter import settings
from thunter.constants import (
    CURRENT_TASK_IDENTIFIER,
    HISTORY_TABLE,
    TASKS_TABLE,
    Status,
    ThunterCouldNotFindTaskError,
    ThunterFoundMultipleTasksError,
    ThunterNotInitializedError,
)
from thunter.models.task import Task
from thunter.models.task_history_record import TaskHistoryRecord


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
        self, task_identifier: Union[str, int], statuses: Optional[set[Status]] = None
    ) -> Task:
        params: list[str] = []
        if isinstance(task_identifier, int) or task_identifier.isdigit():
            where_clause = "id=?"
            order_by = "last_modified DESC"
            params = [str(task_identifier)]
        elif task_identifier == CURRENT_TASK_IDENTIFIER:
            where_clause = None
            order_by = "last_modified DESC"
            params = []
        elif task_identifier:
            where_clause = "name LIKE ?"
            order_by = "last_modified DESC"
            params = [task_identifier + "%"]
        else:
            raise AssertionError("No task identifier given.")

        if statuses:
            if where_clause:
                where_clause += " AND status IN (" + ",".join(len(statuses) * "?") + ")"
            else:
                where_clause = "status IN (" + ",".join(len(statuses) * "?") + ")"

            params.extend(map(lambda s: s.value, statuses))

        tasks = self.select_from_task(
            where_clause=where_clause, order_by=order_by, params=params
        )

        if len(tasks) == 0:
            raise ThunterCouldNotFindTaskError(
                f"Could not find task for identifier: [yellow]{task_identifier}[/yellow]"
            )
        elif len(tasks) > 1:
            if task_identifier == CURRENT_TASK_IDENTIFIER:
                return tasks[0]
            raise ThunterFoundMultipleTasksError(
                f"Found multiple tasks for identifier: [yellow]{task_identifier}[/yellow]"
            )

        return tasks[0]

    def display_task(self, taskid):
        task = self.get_task(str(taskid))
        task_history = self.get_history(taskid)

        lines = []
        lines.append("NAME: %s" % task.name)
        lines.append("ESTIMATE: %s" % task.estimate)
        lines.append("STATUS: %s" % task.status.value)
        lines.append("DESCRIPTION: %s" % task.description)
        lines.append("")
        lines.append("HISTORY")
        for history_record in task_history:
            record_type = "Start" if history_record.is_start else "Stop"
            lines.append(record_type + "\t" + history_record.time_display)
        return "\n".join(lines + [""])

    def create_task(
        self,
        name: str,
        estimate: Optional[int] = None,
        description: Optional[str] = None,
        status: Status = Status.TODO,
    ) -> Task:
        new_task_id = self.insert_task(
            name, estimate, description, status, last_modified=now()
        )
        return self.get_task(new_task_id)

    def get_tasks(
        self,
        statuses: Optional[set[Status]] = None,
        starts_with: Optional[str] = None,
        contains: Optional[str] = None,
    ) -> list[Task]:
        where_clause_param_tuples = []
        if starts_with:
            where_clause_param_tuples.append(("name LIKE ?", (starts_with + "%",)))
        if contains:
            where_clause_param_tuples.append(("name LIKE ?", ("%" + contains + "%",)))
        if statuses:
            where_clause_param_tuples.append(
                (
                    "status IN (" + ",".join(len(statuses) * "?") + ")",
                    map(lambda s: s.value, statuses),
                )
            )
        if where_clause_param_tuples:
            where_clauses, where_params = zip(*where_clause_param_tuples)
            where_clause = " AND ".join(where_clauses)
            params = [param for params in where_params for param in params]
        else:
            where_clause = None
            params = None

        tasks = self.select_from_task(where_clause=where_clause, params=params)
        return sorted(tasks)

    def get_history(self, taskids):
        if isinstance(taskids, int):
            taskids = [taskids]
        assert all(map(lambda taskid: isinstance(taskid, int), taskids))

        where_clause = "taskid IN (" + ",".join(len(taskids) * "?") + ")"
        history = self.select_from_history(where_clause=where_clause, params=taskids)
        return sorted(history)

    def get_progress(self, taskid):
        history = self.get_history(taskid)
        return TaskHistoryRecord.calc_progress(history)

    def get_current_task(self):
        current_tasks = self.select_from_task(
            where_clause="status IN (?)",
            params=[Status.CURRENT.value],
        )
        if len(current_tasks) == 0:
            return None
        elif len(current_tasks) > 1:
            raise AssertionError("More than one current task? How!?")

        return current_tasks[0]

    def workon_task(self, task_identifier: Union[str, int]) -> None:
        task = self.get_task(task_identifier)
        current_task = self.get_current_task()
        if current_task:
            if current_task.id == task.id:
                return
            self.insert_history(taskid=current_task.id, is_start=False, time=now())
            self.update_task(current_task.id, "status", Status.IN_PROGRESS.value)
        self.insert_history(taskid=task.id, is_start=True, time=now())
        self.update_task(task.id, "status", Status.CURRENT.value)

    def stop_current_task(self) -> Optional[Task]:
        current_task = self.get_current_task()
        if not current_task:
            return
        self.insert_history(taskid=current_task.id, is_start=False, time=now())
        self.update_task(current_task.id, "status", Status.IN_PROGRESS.value)
        return self.get_task(current_task.id)

    def finish_task(self, taskid):
        self.update_task(taskid, "status", Status.FINISHED.value)

    def estimate_task(self, taskid, estimate):
        self.update_task(taskid, "estimate", estimate)

    def remove_task(self, taskid):
        delete_task_sql = "DELETE from {table} WHERE id=?".format(table=TASKS_TABLE)
        delete_history_sql = "DELETE from {table} WHERE taskid=?".format(
            table=HISTORY_TABLE
        )
        self.execute(delete_task_sql, (taskid,))
        self.execute(delete_history_sql, (taskid,))

    def update_task(self, taskid: int, field: str, value: Union[str, int]):
        sql = ("UPDATE {table} SET {field}=?, last_modified=? " "WHERE id=?").format(
            table=TASKS_TABLE, field=field
        )
        self.execute(sql, (value, now(), taskid))

    def select_from_task(
        self,
        where_clause: Optional[str] = None,
        order_by: Optional[str] = None,
        params: Optional[list[str]] = None,
    ):
        return list(
            map(
                Task.from_db_record,
                self.select_from_table(TASKS_TABLE, where_clause, order_by, params),
            )
        )

    def select_from_history(self, where_clause=None, order_by=None, params=None):
        return list(
            map(
                TaskHistoryRecord.from_db_record,
                self.select_from_table(HISTORY_TABLE, where_clause, order_by, params),
            )
        )

    def select_from_table(self, table, where_clause=None, order_by=None, params=None):
        assert table in (TASKS_TABLE, HISTORY_TABLE)
        sql = "SELECT * FROM {table}".format(table=table)
        if where_clause:
            sql += " WHERE " + where_clause
        if order_by:
            sql += " ORDER BY " + order_by

        with self.connect() as conn:
            return conn.execute(sql, params or []).fetchall()

    def insert_task(
        self,
        name: str,
        estimate: Optional[int],
        description: Optional[str],
        status: Status,
        last_modified: int,
    ) -> int:
        sql = (
            "INSERT INTO {table} "
            "(name,estimate,description,status,last_modified) "
            "VALUES (?,?,?,?,?)"
        ).format(table=TASKS_TABLE)
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

    def insert_history(self, taskid: int, is_start: bool, time: int):
        sql = ("INSERT INTO {table} (taskid,is_start,time) VALUES " "(?,?,?)").format(
            table=HISTORY_TABLE
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
