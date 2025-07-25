from os import environ
from os import path


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
