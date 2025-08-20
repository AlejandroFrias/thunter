from dataclasses import dataclass
from time import time
from functools import total_ordering

from thunter.time import display_time


@total_ordering
@dataclass
class TaskHistoryRecord:
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
    def calc_progress(cls, task_history: list["TaskHistoryRecord"]) -> int:
        """Calculates the total time (seconds) spent on a task based on its history records."""
        progress = 0
        start_time = 0
        for history_record in sorted(task_history):
            if history_record.is_start:
                start_time = history_record.time
            else:
                progress += history_record.time - start_time
                start_time = 0
        if task_history and start_time:
            progress += int(time()) - start_time
        return progress

    @classmethod
    def display_progress(cls, seconds: int) -> str:
        """Formats the progress time (int seconds) in HH:MM:SS format."""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)

    @property
    def time_display(self) -> str:
        return display_time(self.time)

    def __lt__(self, other: "TaskHistoryRecord"):
        return (self.taskid, self.time, not self.is_start) < (
            other.taskid,
            other.time,
            not other.is_start,
        )

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id
