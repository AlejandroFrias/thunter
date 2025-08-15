from unittest import TestCase

from thunter.constants import (
    Status,
    ThunterCouldNotFindTaskError,
    ThunterFoundMultipleTasksError,
)
from thunter.task_hunter import TaskHunter
from thunter.tests import setUpTestDatabase, tearDownTestDatabase


class TestTaskHunter(TestCase):
    def setUp(self):
        self.env = setUpTestDatabase()
        self.thunter = TaskHunter()

    def tearDown(self):
        """Remove the temporary environment and database after tests."""
        tearDownTestDatabase(self.env)

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

        default_recent_task = self.thunter.get_task()
        self.assertEqual(default_recent_task.id, default_current_task.id)

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

    def test_create_task_invalid_name(self):
        with self.assertRaises(ValueError) as exception:
            self.thunter.create_task(
                name="123",
                estimate=5,
                description="Invalid number-only task name.",
                status=Status.TODO,
            )
        self.assertEqual(
            str(exception.exception),
            "Task cannot be a number, as that would conflict with task IDs.",
        )

    def test_get_tasks(self):
        tasks = self.thunter.get_tasks()
        self.assertEqual(len(tasks), 6)
        self.assertIn("a test task", [task.name for task in tasks])
        self.assertIn("a finished task", [task.name for task in tasks])
        self.assertIn("a long task", [task.name for task in tasks])

        starts_with_a_tasks = self.thunter.get_tasks(starts_with="a")
        self.assertEqual(len(starts_with_a_tasks), 4)
        self.assertIn("a test task", [task.name for task in starts_with_a_tasks])
        self.assertIn("a finished task", [task.name for task in starts_with_a_tasks])

        contains_great_task = self.thunter.get_tasks(contains="great")
        self.assertEqual(len(contains_great_task), 1)
        self.assertEqual(contains_great_task[0].name, "another great test task")

        todo_tasks = self.thunter.get_tasks(statuses={Status.TODO})
        self.assertEqual(len(todo_tasks), 3)
        self.assertEqual(
            [
                "another great test task",
                "identically named task",
                "identically named task",
            ],
            sorted([task.name for task in todo_tasks]),
        )

    def test_workon_task(self):
        current_task = self.thunter.get_task()
        self.assertEqual(current_task.name, "a long task")
        self.assertEqual(current_task.status, Status.CURRENT)
        current_task_history = self.thunter.get_history([current_task.id])

        next_task = self.thunter.get_task(task_identifier="a test task")
        next_task_history = self.thunter.get_history([next_task.id])

        # Start working on the next task
        self.thunter.workon_task(next_task.id)

        new_current_task = self.thunter.get_task()
        self.assertEqual(new_current_task, next_task)

        previously_current_task = self.thunter.get_task(current_task.id)
        previously_current_task_history = self.thunter.get_history(
            [previously_current_task.id]
        )
        new_current_task_history = self.thunter.get_history([new_current_task.id])

        self.assertEqual(len(new_current_task_history), len(next_task_history) + 1)
        self.assertEqual(
            len(previously_current_task_history), len(current_task_history) + 1
        )
        self.assertEqual(new_current_task.status, Status.CURRENT)
        self.assertEqual(previously_current_task.status, Status.IN_PROGRESS)

        # Already working on this task, should be a no-op
        self.thunter.workon_task(1)

        unchanged_current_task = self.thunter.get_task()
        unchanged_current_task_history = self.thunter.get_history(
            [unchanged_current_task.id]
        )
        self.assertEqual(unchanged_current_task, new_current_task)
        self.assertEqual(unchanged_current_task.status, new_current_task.status)
        self.assertEqual(unchanged_current_task_history, new_current_task_history)

    def test_stop_current_task(self):
        current_task = self.thunter.get_current_task()
        self.assertIsNotNone(current_task)
        assert current_task

        current_history = self.thunter.get_history([current_task.id])
        self.assertEqual(current_task.status, Status.CURRENT)
        self.assertEqual(len(current_history), 3)

        stopped_task = self.thunter.stop_current_task()
        assert stopped_task

        self.assertEqual(stopped_task.id, current_task.id)
        self.assertEqual(stopped_task.status, Status.IN_PROGRESS)

        # Verify the task is no longer current
        self.assertIsNone(self.thunter.get_current_task())

        # Verify the task history was updated
        stopped_history = self.thunter.get_history([stopped_task.id])
        self.assertEqual(len(stopped_history), len(current_history) + 1)

        # stopping the current task again should not change anything
        self.assertIsNone(self.thunter.stop_current_task())

    def test_update_finish_task(self):
        current_task = self.thunter.get_task()
        current_history = self.thunter.get_history([current_task.id])
        self.assertEqual(current_task.status, Status.CURRENT)

        self.thunter.finish_task(current_task.id)

        finished_task = self.thunter.get_task(current_task.id)
        self.assertEqual(finished_task.status, Status.FINISHED)

        # Verify the task history was updated
        finished_history = self.thunter.get_history([finished_task.id])
        self.assertEqual(len(finished_history), len(current_history) + 1)

    def test_estimate_task(self):
        current_task = self.thunter.get_task()
        self.assertEqual(current_task.estimate, 32)

        self.thunter.estimate_task(taskid=current_task.id, estimate=10)

        updated_task = self.thunter.get_task(current_task.id)
        self.assertEqual(updated_task.estimate, 10)

    def test_remove_task(self):
        current_task = self.thunter.get_task()
        self.thunter.remove_task(current_task.id)
        with self.assertRaises(ThunterCouldNotFindTaskError):
            self.thunter.get_task(current_task.id)
