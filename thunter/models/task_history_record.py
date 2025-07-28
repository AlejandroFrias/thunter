from time import time
from functools import total_ordering
from typing import NamedTuple

from thunter.constants import display_time


@total_ordering
class TaskHistoryRecord(NamedTuple):
    """Represents a task history record, used to track time spent working on the task."""

    id: int
    taskid: int
    is_start: bool
    time: int

    @classmethod
    def from_db_record(cls, record: tuple[int, int, bool, int]):
        return cls(
            id=record[0], taskid=record[1], is_start=bool(record[2]), time=record[3]
        )

    @classmethod
    def calc_progress(cls, task_history):
        """Calculates the total time spent on a task based on its history records."""
        progress = 0
        start_time = None
        for history_record in task_history:
            if bool(history_record.is_start):
                start_time = history_record.time
            else:
                progress += history_record.time - start_time
                start_time = None
        if task_history and start_time:
            progress += int(time()) - start_time
        return progress

    @classmethod
    def display_progress(cls, seconds):
        """Formats the progress time (int seconds) in HH:MM:SS format."""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)

    @property
    def time_display(self):
        return display_time(self.time)

    def __str__(self):
        return "{id} {verb} at {time}".format(
            id=self.id,
            verb=("Started" if self.is_start else "Stopped"),
            time=self.time_display,
        )

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return (self.taskid, self.time, not self.is_start) < (
            other.taskid,
            other.time,
            not other.is_start,
        )

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id
