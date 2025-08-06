from unittest import TestCase

from thunter.constants import Status, ThunterTaskValidationError
from thunter.models import Task, TaskHistoryRecord
from thunter.task_parser import (
    ParsedTaskData,
    ParsedTaskHistoryRecord,
    display_task,
    parse_task_display,
    validate_task_data,
)


class TestTaskParser(TestCase):
    def test_parse_task(self):
        """Test parsing a task from a string."""
        task = Task(
            id=1,
            name="Test Task",
            description="This is a test task.",
            estimate=4,
            status=Status.IN_PROGRESS,
            last_modified_at=1633036800,
            created_at=1633036800,
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

        task_without_history_display = (
            "NAME: Test Task\n"
            "ESTIMATE: 4\n"
            "STATUS: TODO\n"
            "DESCRIPTION: This is a test task.\n"
            "\n"
            "HISTORY\n"
        )

        parsed_data_without_history = parse_task_display(task_without_history_display)

        self.assertEqual(parsed_data_without_history.name, "Test Task")
        self.assertEqual(parsed_data_without_history.estimate, 4)
        self.assertEqual(
            parsed_data_without_history.description, "This is a test task."
        )
        self.assertEqual(parsed_data_without_history.status, Status.TODO)
        self.assertEqual(len(parsed_data_without_history.history), 0)

    def test_validate_task_data(self):
        """Test validating task data."""
        task_data = ParsedTaskData(
            name="TODO task with history!",
            estimate=3,
            description="A valid task for testing.",
            status=Status.TODO,
            history=[
                ParsedTaskHistoryRecord(is_start=True, time=1633036800),
                ParsedTaskHistoryRecord(is_start=False, time=1633037200),
            ],
        )
        with self.assertRaises(ThunterTaskValidationError) as error:
            validate_task_data(task_data)
        self.assertIn(
            "Can't have a history if the status is TODO", str(error.exception)
        )

        task_data = ParsedTaskData(
            name="IN_PROGRESS task without history!",
            estimate=3,
            description=None,
            status=Status.IN_PROGRESS,
            history=[],
        )
        with self.assertRaises(ThunterTaskValidationError) as error:
            validate_task_data(task_data)
        self.assertIn(
            "Must have a history if status is In Progress", str(error.exception)
        )

        task_data = ParsedTaskData(
            name="CURRENT task that isn't tracking time!",
            estimate=3,
            description=None,
            status=Status.CURRENT,
            history=[
                ParsedTaskHistoryRecord(is_start=True, time=1633036800),
                ParsedTaskHistoryRecord(is_start=False, time=1633037200),
            ],
        )
        with self.assertRaises(ThunterTaskValidationError) as error:
            validate_task_data(task_data)
        self.assertIn(
            "Last history record must be a Start if the status is Current",
            str(error.exception),
        )

        task_data = ParsedTaskData(
            name="IN_PROGRESS task that is tracking time!",
            estimate=3,
            description=None,
            status=Status.IN_PROGRESS,
            history=[
                ParsedTaskHistoryRecord(is_start=True, time=1633036800),
            ],
        )
        with self.assertRaises(ThunterTaskValidationError) as error:
            validate_task_data(task_data)
        self.assertIn(
            "Last history record must be a Stop if the status is In Progress",
            str(error.exception),
        )

        task_data = ParsedTaskData(
            name="FINISHED task that is tracking time!",
            estimate=3,
            description=None,
            status=Status.FINISHED,
            history=[
                ParsedTaskHistoryRecord(is_start=True, time=1633036800),
            ],
        )
        with self.assertRaises(ThunterTaskValidationError) as error:
            validate_task_data(task_data)
        self.assertIn(
            "Last history record must be a Stop if the status is Finished",
            str(error.exception),
        )

        task_data = ParsedTaskData(
            name="Out of order history",
            estimate=3,
            description=None,
            status=Status.FINISHED,
            history=[
                ParsedTaskHistoryRecord(is_start=True, time=1633036805),
                ParsedTaskHistoryRecord(is_start=False, time=1633036800),
            ],
        )
        with self.assertRaises(ThunterTaskValidationError) as error:
            validate_task_data(task_data)
        self.assertIn(
            "History must be in ascending order by time",
            str(error.exception),
        )

        task_data = ParsedTaskData(
            name="Stop and Start reversed",
            estimate=3,
            description=None,
            status=Status.FINISHED,
            history=[
                ParsedTaskHistoryRecord(is_start=True, time=1633036800),
                ParsedTaskHistoryRecord(is_start=True, time=1633036800),
                ParsedTaskHistoryRecord(is_start=False, time=1633036800),
                ParsedTaskHistoryRecord(is_start=False, time=1633036800),
            ],
        )
        with self.assertRaises(ThunterTaskValidationError) as error:
            validate_task_data(task_data)
        self.assertIn(
            "History must alternate between Start and Stop",
            str(error.exception),
        )
