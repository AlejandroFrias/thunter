import calendar
from dataclasses import dataclass
from time import strptime
from typing import TypeGuard

import pyparsing as pp

from thunter.constants import TIME_FORMAT, ThunterTaskValidationError, Status
from thunter.models import Task, TaskHistoryRecord


@dataclass
class ParsedTaskHistoryRecord:
    is_start: bool
    time: int


@dataclass
class ParsedTaskData:
    name: str
    estimate: int | None
    description: str | None
    status: Status
    history: list[ParsedTaskHistoryRecord]


def parse_time(t: pp.ParseResults) -> int:
    """parser action for converting time string to seconds"""
    if isinstance(t.time, str):
        return calendar.timegm(strptime(t.time, TIME_FORMAT))
    raise ValueError


word = pp.Word(pp.alphanums + " .!?&-_()")
number = pp.common.integer
status_type = pp.one_of([s.value for s in Status]).set_parse_action(
    lambda t: Status(t.status)
)
is_start = pp.one_of(["Start", "Stop"])("is_start").set_parse_action(
    lambda t: t[0] == "Start"
)
time = pp.Word(pp.nums + " -:")("time").set_parse_action(parse_time)
name = pp.Suppress("NAME:") + word("name")
estimate = pp.Suppress("ESTIMATE:") + number("estimate")
status = pp.Suppress("STATUS:") + status_type("status")


description = pp.Suppress("DESCRIPTION:") + pp.rest_of_line(
    "description"
).set_parse_action(
    lambda t: t.description.strip() if isinstance(t.description, str) else ""
)

history_record = pp.Group(is_start("is_start") + time("time"))
history = pp.Suppress(pp.Keyword("HISTORY")) + pp.ZeroOrMore(history_record)("history")

task = name + estimate + status + description + history


def is_parsed_history(history) -> TypeGuard[list[ParsedTaskHistoryRecord]]:
    return all(
        history_record.is_start in [True, False]
        and isinstance(history_record.time, int)
        for history_record in history
    )


def is_parsed_task(data) -> TypeGuard[ParsedTaskData]:
    return (
        isinstance(data.name, str)
        and isinstance(data.estimate, (int, type(None)))
        and isinstance(data.description, (str, type(None)))
        and isinstance(data.status, Status)
        and is_parsed_history(data.history)
    )


def parse_task_display(task_display: str) -> ParsedTaskData:
    """Parses a task's display string into the data necessary to create the task and it's history"""
    task_data = task.parse_string(task_display)

    if not (is_parsed_task(task_data)):
        raise AssertionError("Invalid parsed task data")

    validate_task_data(task_data)
    return task_data


def thunter_assert(expr, message):
    if not expr:
        error_message = f"[red]Task Validation Error:[/red] {message}"
        raise ThunterTaskValidationError(error_message)


def validate_task_data(task_data: ParsedTaskData) -> None:
    if task_data.status == Status.TODO:
        thunter_assert(
            len(task_data.history) == 0, "Can't have a history if the status is TODO"
        )
    else:
        thunter_assert(
            len(task_data.history) > 0,
            "Must have a history if status is %s" % task_data.status.value,
        )

    if task_data.status == Status.CURRENT:
        last_history_record = task_data.history[-1]
        thunter_assert(
            last_history_record.is_start,
            "Last history record must be a Start if the status is Current",
        )
    elif task_data.status in [Status.IN_PROGRESS, Status.FINISHED]:
        last_history_record = task_data.history[-1]
        thunter_assert(
            not last_history_record.is_start,
            "Last history record must be a Stop if the status is %s"
            % task_data.status.value,
        )

    expect_start = True
    last_history_time = 0
    for history_data in task_data.history:
        thunter_assert(
            last_history_time <= history_data.time,
            "History must be in ascending order by time",
        )
        thunter_assert(
            history_data.is_start == expect_start,
            "History must alternate between Start and Stop",
        )
        expect_start = not expect_start
        last_history_time = history_data.time


def display_task(task: Task, task_history: list[TaskHistoryRecord]) -> str:
    """Displays a task in a human-readable and parser friendly format."""
    lines = []
    lines.append("NAME: %s" % task.name)
    lines.append("ESTIMATE: %s" % task.estimate)
    lines.append("STATUS: %s" % task.status.value)
    lines.append("DESCRIPTION: %s" % task.description)
    lines.append("")
    lines.append("HISTORY")
    for history_record in task_history:
        record_type = "Start" if history_record.is_start else "Stop"
        lines.append(record_type + "\t" + history_record.time_display)
    return "\n".join(lines + [""])
