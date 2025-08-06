from unittest import TestCase

from thunter.constants import Status
from thunter.db import Database
from thunter.models.task import Task
from thunter.models.task_history_record import TaskHistoryRecord
from thunter.tests import setUpTestDatabase, tearDownTestDatabase


class TestTaskHunter(TestCase):
    def setUp(self):
        self.env = setUpTestDatabase()
        self.database = Database()

    def tearDown(self):
        """Remove the temporary environment and database after tests."""
        tearDownTestDatabase(self.env)

    def test__init__(self):
        thunter = Database()
        self.assertEqual(thunter.database, self.env.DATABASE)

        thunter = Database("/database.db")
        self.assertEqual(thunter.database, "/database.db")

    def test_select_from_history(self):
        history = self.database.select_from_history(
            where_clause="taskid = ?",
            order_by="time ASC",
            params=["1"],
        )
        expected_history = [
            TaskHistoryRecord(id=3, taskid=1, is_start=True, time=1722208103),
            TaskHistoryRecord(id=4, taskid=1, is_start=False, time=1753732126),
        ]
        self.assertEqual(history, expected_history)

    def test_select_from_task(self):
        history = self.database.select_from_task(
            where_clause="id = ?",
            order_by="id ASC",
            params=["1"],
        )
        expected_history = [
            Task(
                id=1,
                name="a test task",
                estimate=4,
                description=None,
                status=Status.IN_PROGRESS,
                last_modified_at=1753732126,
                created_at=1753732126,
            ),
        ]
        self.assertEqual(history, expected_history)
