from functools import total_ordering
from typing import NamedTuple

from thunter.constants import (
    STATUS_ORDERING,
    Status,
    display_time,
)


# task identifiers can be their ID or their name
TaskIdentifier = int | str


@total_ordering
class Task(NamedTuple):
    """Represents a task in the THunter application."""

    id: int
    name: str
    estimate: int | None
    description: str | None
    status: Status
    last_modified: int

    @classmethod
    def from_db_record(cls, record: tuple[int, str, int | None, str | None, str, int]):
        return cls(
            id=record[0],
            name=record[1],
            estimate=record[2],
            description=record[3],
            status=Status(record[4]),
            last_modified=record[5],
        )

    @property
    def last_modified_display(self):
        return display_time(self.last_modified)

    @property
    def estimate_display(self):
        estimate_display_str = ""
        if self.estimate is not None:
            estimate_display_str = "%d hr" % self.estimate
            if self.estimate > 1:
                estimate_display_str += "s"
        return estimate_display_str

    def __str__(self):
        return "{name} ({status}): {desc}".format(
            name=self.name, status=self.status, desc=self.description
        )

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return (STATUS_ORDERING.index(self.status.value), -self.last_modified) < (
            STATUS_ORDERING.index(other.status.value),
            -other.last_modified,
        )

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id
