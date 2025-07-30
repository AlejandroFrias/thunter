from dataclasses import dataclass
import os
import shutil
import sqlite3
import tempfile

from thunter import settings
from thunter.task_hunter import TaskHunter


@dataclass
class TestDatabaseEnvironment:
    THUNTER_DIR: str
    DATABASE: str


def setUpTestDatabase() -> TestDatabaseEnvironment:
    """Setup a temporary environment and database for testing."""
    thunter_dir = tempfile.mkdtemp()
    env = TestDatabaseEnvironment(
        THUNTER_DIR=thunter_dir,
        DATABASE=os.path.join(thunter_dir, "test_database.db"),
    )
    settings.THUNTER_DIR = env.THUNTER_DIR
    settings.DATABASE = env.DATABASE

    conn = sqlite3.connect(env.DATABASE)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + "/test_database_fixture.sql", "r") as f:
        conn.executescript(f.read())

    return env


def tearDownTestDatabase(env: TestDatabaseEnvironment) -> None:
    """Remove the temporary environment and database after tests."""
    shutil.rmtree(env.THUNTER_DIR)
