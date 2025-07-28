import os
import shutil
import sqlite3
import tempfile
from unittest import TestCase


from thunter import settings
from thunter.constants import (
    CURRENT_TASK_IDENTIFIER,
    Status,
    ThunterCouldNotFindTaskError,
)
from thunter.task_hunter import TaskHunter


class TestTaskHunter(TestCase):
    def setUp(self):
        """Setup a temporary environment and database for testing."""
        thunter_dir = tempfile.mkdtemp()
        self.env = {
            "THUNTER_DIR": thunter_dir,
            "DATABASE": os.path.join(thunter_dir, "test_database.db"),
        }
        settings.THUNTER_DIR = self.env["THUNTER_DIR"]
        settings.DATABASE = self.env["DATABASE"]

        conn = sqlite3.connect(self.env["DATABASE"])
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + "/test_database_fixture.sql", "r") as f:
            conn.executescript(f.read())

    def tearDown(self):
        """Remove the temporary environment and database after tests."""
        shutil.rmtree(self.env["THUNTER_DIR"])

    def test_dunder_init(self):
        thunter = TaskHunter()
        self.assertEqual(thunter.database, self.env["DATABASE"])

        thunter = TaskHunter("/database.db")
        self.assertEqual(thunter.database, "/database.db")

    def test_get_task_by_id(self):
        thunter = TaskHunter()
        task_by_id = thunter.get_task(1)
        self.assertEqual(task_by_id.name, "a test task")
        self.assertEqual(task_by_id.status, Status.IN_PROGRESS)

        with self.assertRaises(ThunterCouldNotFindTaskError):
            thunter.get_task(-1)

    def test_get_task_by_name(self):
        thunter = TaskHunter()
        task_by_name = thunter.get_task("a test task")
        self.assertEqual(task_by_name.id, 1)
        self.assertEqual(task_by_name.name, "a test task")
        self.assertEqual(task_by_name.status, Status.IN_PROGRESS)

        with self.assertRaises(ThunterCouldNotFindTaskError):
            thunter.get_task("nonexistent task")

    def test_get_current_task(self):
        thunter = TaskHunter()
        current_task = thunter.get_task(CURRENT_TASK_IDENTIFIER)
        self.assertEqual(current_task.id, 5)
        self.assertEqual(current_task.name, "a long task")
        self.assertEqual(current_task.status, Status.CURRENT)

        with self.assertRaises(AssertionError):
            thunter.get_task("")

    def test_get_finished_task(self):
        thunter = TaskHunter()
        finished_task = thunter.get_task("a finished task")
        self.assertEqual(finished_task.id, 4)
        self.assertEqual(finished_task.name, "a finished task")
        self.assertEqual(finished_task.status, Status.FINISHED)

        with self.assertRaises(ThunterCouldNotFindTaskError):
            thunter.get_task(finished_task.id, statuses={Status.TODO})
