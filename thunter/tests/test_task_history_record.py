from unittest import TestCase

from thunter.models import TaskHistoryRecord


class TestTaskHistoryRecord(TestCase):
    def test_from_db_record(self):
        """Test creating a task from a database record."""
        record = (1, 2, True, 1633036800)
        task = TaskHistoryRecord.from_db_record(record)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.taskid, 2)
        self.assertEqual(task.is_start, True)
        self.assertEqual(task.time, 1633036800)
        self.assertEqual(task.time_display, "2021-09-30 21:20:00")

    def test_calc_progress(self):
        """Test calculating progress from task history records."""
        history = [
            TaskHistoryRecord(id=2, taskid=1, is_start=False, time=1633021171),
            TaskHistoryRecord(id=4, taskid=1, is_start=False, time=1633021260),
            TaskHistoryRecord(id=1, taskid=1, is_start=True, time=1633021111),
            TaskHistoryRecord(id=3, taskid=1, is_start=True, time=1633021200),
        ]
        progress = TaskHistoryRecord.calc_progress(history)
        self.assertEqual(progress, 120)

    def test_display_progress(self):
        """Test displaying progress in HH:MM:SS format."""
        seconds = 3661
        formatted_progress = TaskHistoryRecord.display_progress(seconds)
        self.assertEqual(formatted_progress, "01:01:01")

    def test_ordering(self):
        """Test ordering of tasks based on statuses and last modified time."""
        history_record1 = TaskHistoryRecord(
            id=1,
            taskid=1,
            is_start=True,
            time=1633021111,
        )
        history_record2 = TaskHistoryRecord(
            id=2,
            taskid=1,
            is_start=False,
            time=1633021171,
        )
        history_record3 = TaskHistoryRecord(
            id=3,
            taskid=2,
            is_start=True,
            time=1633021111,
        )
        history_record4 = TaskHistoryRecord(
            id=4,
            taskid=2,
            is_start=False,
            time=1633021111,
        )

        sorted_history = sorted(
            [history_record4, history_record3, history_record2, history_record1]
        )
        self.assertEqual(
            sorted_history,
            [history_record1, history_record2, history_record3, history_record4],
        )
