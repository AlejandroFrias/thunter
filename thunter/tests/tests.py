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
    ThunterFoundMultipleTasksError,
    ThunterNotInitializedError,
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

        self.thunter = TaskHunter()

    def tearDown(self):
        """Remove the temporary environment and database after tests."""
        shutil.rmtree(self.env["THUNTER_DIR"])

    def test__init__(self):
        thunter = TaskHunter()
        self.assertEqual(thunter.database, self.env["DATABASE"])

        thunter = TaskHunter("/database.db")
        self.assertEqual(thunter.database, "/database.db")

        settings.DATABASE = None
        with self.assertRaises(ThunterNotInitializedError):
            TaskHunter()

    def test_get_task_by_id(self):
        task_by_id = self.thunter.get_task(1)
        self.assertEqual(task_by_id.name, "a test task")
        self.assertEqual(task_by_id.status, Status.IN_PROGRESS)

        with self.assertRaises(ThunterCouldNotFindTaskError):
            self.thunter.get_task(-1)

    def test_get_task_by_name(self):
        task_by_name = self.thunter.get_task("a test task")
        self.assertEqual(task_by_name.id, 1)
        self.assertEqual(task_by_name.name, "a test task")
        self.assertEqual(task_by_name.status, Status.IN_PROGRESS)

        with self.assertRaises(ThunterCouldNotFindTaskError):
            self.thunter.get_task("nonexistent task")

        with self.assertRaises(ThunterFoundMultipleTasksError):
            self.thunter.get_task("identically named task")

    def test_get_current_task(self):
        default_current_task = self.thunter.get_task()
        self.assertEqual(default_current_task.id, 5)
        self.assertEqual(default_current_task.name, "a long task")
        self.assertEqual(default_current_task.status, Status.CURRENT)

        current_task = self.thunter.get_current_task()
        self.assertEqual(current_task, default_current_task)

        stopped_current_task = self.thunter.stop_current_task()
        self.assertEqual(stopped_current_task.id, current_task.id)  # type: ignore
        self.assertEqual(self.thunter.get_current_task(), None)
        with self.assertRaises(ThunterCouldNotFindTaskError):
            self.thunter.get_task()

    def test_get_finished_task(self):
        finished_task = self.thunter.get_task("a finished task")
        self.assertEqual(finished_task.id, 4)
        self.assertEqual(finished_task.name, "a finished task")
        self.assertEqual(finished_task.status, Status.FINISHED)

        with self.assertRaises(ThunterCouldNotFindTaskError):
            self.thunter.get_task(finished_task.id, statuses={Status.TODO})

    def test_display_task(self):
        task_display = self.thunter.display_task(1)
        self.assertEqual(
            task_display,
            "NAME: a test task\n"
            "ESTIMATE: 4\n"
            "STATUS: In Progress\n"
            "DESCRIPTION: None\n"
            "\n"
            "HISTORY\n"
            "Start\t2025-07-28 19:48:23\n"
            "Stop\t2025-07-28 19:48:46\n",
        )

    def test_create_task(self):
        new_task = self.thunter.create_task(
            name="New Task",
            estimate=5,
            description="A new task for testing.",
            status=Status.TODO,
        )
        self.assertEqual(new_task.name, "New Task")
        self.assertEqual(new_task.estimate, 5)
        self.assertEqual(new_task.description, "A new task for testing.")
        self.assertEqual(new_task.status, Status.TODO)

        # Verify the task was added to the database
        fetched_task = self.thunter.get_task(new_task.id)
        self.assertEqual(fetched_task, new_task)
