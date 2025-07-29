from unittest import TestCase

from thunter.constants import Status
from thunter.models import Task, TaskHistoryRecord
from thunter.task_parser import display_task, parse_task_display


class TestTaskParser(TestCase):
    def test_parse_task(self):
        """Test parsing a task from a string."""
        task = Task(
            id=1,
            name="Test Task",
            description="This is a test task.",
            estimate=4,
            status=Status.IN_PROGRESS,
            last_modified=1633036800,
        )
        task_history = [
            TaskHistoryRecord(
                id=1,
                taskid=1,
                is_start=True,
                time=1633036800,
            ),
            TaskHistoryRecord(
                id=2,
                taskid=1,
                is_start=False,
                time=1633037200,
            ),
        ]
        task_display = display_task(task, task_history)
        expected_display = (
            "NAME: Test Task\n"
            "ESTIMATE: 4\n"
            "STATUS: In Progress\n"
            "DESCRIPTION: This is a test task.\n"
            "\n"
            "HISTORY\n"
            "Start\t2021-09-30 21:20:00\n"
            "Stop\t2021-09-30 21:26:40\n"
        )
        self.assertEqual(task_display, expected_display)

        parsed_data = parse_task_display(task_display)

        self.assertEqual(parsed_data.name, "Test Task")
        self.assertEqual(parsed_data.estimate, 4)
        self.assertEqual(parsed_data.description, "This is a test task.")
        self.assertEqual(parsed_data.status, Status.IN_PROGRESS)
        self.assertEqual(len(parsed_data.history), 2)
        self.assertTrue(parsed_data.history[0].is_start)
        self.assertEqual(parsed_data.history[0].time, 1633036800)
        self.assertFalse(parsed_data.history[1].is_start)
        self.assertEqual(parsed_data.history[1].time, 1633037200)
