from os import environ
from os import path
import os


THUNTER_DIR = path.expanduser(environ.get("THUNTER_DIRECTORY", "~/.thunter"))
DATABASE = path.join(
    THUNTER_DIR, environ.get("THUNTER_DATABASE_NAME", "thunter_database.db")
)
EDITOR = environ.get("EDITOR", "vim")
THUNTER_SILENT = environ.get("THUNTER_SILENT", "false").lower() in (
    "true",
    "1",
    "yes",
    "y",
)
DEBUG = environ.get("DEBUG", "false").lower() in ("true", "1", "yes", "y")


def needs_init():
    """Checks if `thunter init` needs to be run to setup the environment."""
    return (
        not THUNTER_DIR
        or not DATABASE
        or not os.path.exists(THUNTER_DIR)
        or not os.path.exists(DATABASE)
    )
