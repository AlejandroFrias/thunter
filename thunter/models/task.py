from dataclasses import dataclass
from functools import total_ordering

from thunter.constants import (
    STATUS_ORDERING,
    Status,
)
from thunter.time import display_time


# task identifiers can be their ID or their name
TaskIdentifier = int | str


@total_ordering
@dataclass
class Task:
    """Represents a task in the THunter application."""

    id: int
    name: str
    estimate: int | None
    description: str | None
    status: Status
    last_modified_at: int
    created_at: int

    @classmethod
    def from_db_record(
        cls, record: tuple[int, str, int | None, str | None, str, int, int]
    ):
        return cls(
            id=record[0],
            name=record[1],
            estimate=record[2],
            description=record[3],
            status=Status(record[4]),
            last_modified_at=record[5],
            created_at=record[6],
        )

    @property
    def last_modified_at_display(self):
        return display_time(self.last_modified_at)

    @property
    def estimate_display(self):
        estimate_display_str = ""
        if self.estimate is not None:
            estimate_display_str = "%d hr" % self.estimate
            if self.estimate > 1:
                estimate_display_str += "s"
        return estimate_display_str

    def __lt__(self, other):
        return (STATUS_ORDERING.index(self.status.value), -self.last_modified_at) < (
            STATUS_ORDERING.index(other.status.value),
            -other.last_modified_at,
        )

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id
