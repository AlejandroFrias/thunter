from os import environ
from os import path


HUNT_DIR = path.expanduser(environ.get("HUNT_DIRECTORY", "~/.hunt"))
DATABASE = path.join(HUNT_DIR, environ.get("HUNT_DATABASE_NAME", "database.db"))
EDITOR = environ.get("EDITOR", "vim")
HUNT_SILENT = environ.get("HUNT_SILENT", "false").lower() in ("true", "1", "yes", "y")
DEBUG = environ.get("DEBUG", "false").lower() in ("true", "1", "yes", "y")
