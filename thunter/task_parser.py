from dataclasses import dataclass
from typing import TypeGuard
from parsimonious import Grammar, NodeVisitor
from time import strptime
import calendar

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


class TaskVisitor(NodeVisitor):
    grammar: Grammar

    def __init__(self):
        super().__init__()
        print("Initializing TaskVisitor")
        self.grammar = Grammar(
            r"""task = name newline+
estimate newline+
status newline+
description newline+
history newline*
name = "NAME:" whitespace? phrase whitespace?
estimate = "ESTIMATE:" whitespace? int whitespace?
description = "DESCRIPTION:" whitespace? phrase whitespace?
status = "STATUS:" whitespace? status_type whitespace?
status_type = "Current" / "TODO" / "In Progress" / "Finished"
history = whitespace? "HISTORY" whitespace? newline+ history_records?
whitespace = ~"[ \t]+"
newline = "\n" / "\n\r"
phrase = word (whitespace word)*
word = ~"[0-9a-zA-Z.!?&-_]+"
int = ~"[1-9][0-9]*" / "None"
history_records = history_record (next_history_record)*
history_record = history_record_type whitespace time whitespace?
next_history_record = newline+ history_record
history_record_type = "Start" / "Stop"
time = year "-" month "-" day " " hours ":" minutes ":" seconds
year = ~"20[0-9]{2}"
month = ~"0[1-9]" / ~"1[0-2]"
day = ~"0[1-9]" / ~"1[0-9]" / ~"2[0-9]" / ~"3[0-1]"
hours = ~"0[0-9]" / ~"1[0-9]" / ~"2[0-3]"
minutes = ~"[0-5][0-9]"
seconds = minutes
"""
        )
        print("Initialized TaskVisitor")

    def visit_task(self, node, visited_children) -> ParsedTaskData:
        (name, _nl1, estimate, _nl2, status, _nl3, description, _nl4, history, _nl5) = (
            visited_children
        )
        task_data = ParsedTaskData(
            name=name,
            estimate=estimate,
            description=description,
            status=status,
            history=[
                ParsedTaskHistoryRecord(is_start=is_start, time=history_time)
                for is_start, history_time in history
            ],
        )
        validate_task_data(task_data)
        return task_data

    def visit_name(self, node, visited_children):
        (_name, _ws1, phrase, _ws2) = visited_children
        return phrase

    def visit_estimate(self, node, visited_children):
        (_est, _ws1, phrase, _ws2) = visited_children
        return int(phrase) if phrase.isdigit() else None

    def visit_description(self, node, visited_children):
        (_desc, _ws1, phrase, _ws2) = visited_children
        return None if phrase == "None" else phrase

    def visit_status(self, node, visited_children):
        (_status, _ws1, status_type, _ws2) = visited_children
        return status_type

    def visit_status_type(self, node, visited_children):
        return Status(node.text)

    def visit_history(self, node, visited_children):
        (_ws1, _hist, _ws2, _nl, history_records) = visited_children
        return history_records[0] if history_records else []

    def visit_history_records(self, node, visited_children):
        (history_record, rest) = visited_children
        records = [history_record]
        records.extend(rest)
        return records

    def visit_history_record(self, node, visited_children):
        (history_record_type, _ws1, history_time, _ws2) = visited_children
        return (history_record_type, history_time)

    def visit_next_history_record(self, node, visited_children):
        (_nl, history_record) = visited_children
        return history_record

    def visit_history_record_type(self, node, visited_children):
        return node.text == "Start"

    def visit_time(self, node, visited_children):
        return calendar.timegm(strptime(node.text, TIME_FORMAT))

    def visit_phrase(self, node, visited_children):
        return node.text

    def visit_int(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        return visited_children


def parse_task_display(task_display: str) -> ParsedTaskData:
    """Parses a task's display string into the data necessary to create the task and it's history"""
    task_data = TaskVisitor().parse(task_display)
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
            "Must have a history if status is %s" % task_data.status,
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
            "Last history record must be a Stop if the status is %s" % task_data.status,
        )

    expect_start = True
    last_history_time = 0
    for history_data in task_data.history:
        thunter_assert(
            last_history_time < history_data.time,
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
