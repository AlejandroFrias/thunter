from enum import Enum


class TableName(Enum):
    TASKS = "tasks"
    HISTORY = "history"


class Status(Enum):
    CURRENT = "Current"
    IN_PROGRESS = "In Progress"
    TODO = "TODO"
    FINISHED = "Finished"


STATUS_ORDERING = [
    Status.CURRENT.value,
    Status.IN_PROGRESS.value,
    Status.TODO.value,
    Status.FINISHED.value,
]

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class ThunterError(Exception):
    exit_status = 1


class ThunterCouldNotFindTaskError(ThunterError):
    exit_status = 2


class ThunterAlreadyWorkingOnTaskError(ThunterError):
    exit_status = 3


class ThunterNoCurrentTaskError(ThunterError):
    exit_status = 4


class ThunterFoundMultipleTasksError(ThunterError):
    exit_status = 5


class ThunterTaskValidationError(ThunterError):
    exit_status = 6


class ThunterNotInitializedError(ThunterError):
    exit_status = 7
