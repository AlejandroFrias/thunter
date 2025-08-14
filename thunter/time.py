from datetime import datetime
from time import gmtime, strftime

from thunter.constants import TIME_FORMAT


def now_sec() -> int:
    """Returns the current time as integer seconds since epoch."""
    return int(datetime.now().timestamp())


def display_time(seconds: int) -> str:
    """Formats seconds into a datetime string."""
    return strftime(TIME_FORMAT, gmtime(seconds))
