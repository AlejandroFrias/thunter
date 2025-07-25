import os
import shutil
import sqlite3
import tempfile
from unittest import TestCase

import settings
from hunt.task import TaskHunter


class TestHunt(TestCase):
    def setUp(self):
        hunt_dir = tempfile.mkdtemp()
        self.env = {
            "HUNT_DIR": hunt_dir,
            "DATABASE": os.path.join(hunt_dir, "test_database.db"),
        }
        settings.HUNT_DIR = self.env["HUNT_DIR"]
        settings.DATABASE = self.env["DATABASE"]
        sqlite3.connect(self.env["DATABASE"])

    def tearDown(self):
        shutil.rmtree(self.env["HUNT_DIRECTORY"])

    def test_init(self):
        hunt = TaskHunter()
        self.assertEqual(hunt.database, self.env["DATABASE"])

        hunt = TaskHunter("/database.db")
        self.assertEqual(hunt.database, "/database.db")
