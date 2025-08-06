from unittest import TestCase

from thunter.constants import Status
from thunter.models import Task


class TestTask(TestCase):
    def test_from_db_record(self):
        """Test creating a task from a database record."""
        record = (
            1,
            "Test Task",
            2,
            "This is a test task.",
            "TODO",
            1633036800,
            1633036800,
        )
        task = Task.from_db_record(record)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.estimate, 2)
        self.assertEqual(task.description, "This is a test task.")
        self.assertEqual(task.status.value, "TODO")
        self.assertEqual(task.last_modified_at, 1633036800)
        self.assertEqual(task.created_at, 1633036800)
        self.assertEqual(task.estimate_display, "2 hrs")
        self.assertEqual(task.last_modified_at_display, "2021-09-30 21:20:00")

    def test_ordering(self):
        """Test ordering of tasks based on statuses and last modified time."""
        task1 = Task(
            id=1,
            name="Task A",
            estimate=1,
            description="Description A",
            status=Status.TODO,
            last_modified_at=1633011111,
            created_at=1633011111,
        )
        task2 = Task(
            id=2,
            name="Task B",
            estimate=2,
            description="Description B",
            status=Status.IN_PROGRESS,
            last_modified_at=1633022222,
            created_at=1633022222,
        )
        task3 = Task(
            id=3,
            name="Task C",
            estimate=None,
            description="Description C",
            status=Status.FINISHED,
            last_modified_at=1633033333,
            created_at=1633033333,
        )
        task4 = Task(
            id=3,
            name="Task C",
            estimate=None,
            description="Description C",
            status=Status.FINISHED,
            last_modified_at=1633044444,
            created_at=1633044444,
        )

        sorted_tasks = sorted([task4, task3, task2, task1])
        self.assertEqual(sorted_tasks, [task2, task1, task3, task4])
