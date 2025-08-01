import os
from rich.console import Console


THUNTER_DIR = os.path.expanduser(os.environ.get("THUNTER_DIRECTORY", "~/.thunter"))
DATABASE = os.path.join(
    THUNTER_DIR, os.environ.get("THUNTER_DATABASE_NAME", "thunter_database.db")
)
EDITOR = os.environ.get("EDITOR", "vim")
THUNTER_SILENT = os.environ.get("THUNTER_SILENT", "false").lower() in (
    "true",
    "1",
    "yes",
    "y",
)
DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes", "y")

# Global configuration for printing, updatable by CLI options and initialized
# from environment variables or defaults above.
print_config = {"silent": THUNTER_SILENT, "debug": DEBUG}


def thunter_print(*args, **kwargs):
    """Prints to console if not in silent mode."""
    if not THUNTER_SILENT and not print_config["silent"]:
        console = Console()
        console.print(*args, **kwargs)


def needs_init():
    """Checks if `thunter init` needs to be run to setup the environment."""
    return (
        not THUNTER_DIR
        or not DATABASE
        or not os.path.exists(THUNTER_DIR)
        or not os.path.exists(DATABASE)
    )
