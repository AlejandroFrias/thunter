import os
import shutil
import sqlite3
import tempfile
from unittest import TestCase

import settings
from thunter.task import TaskHunter


class TestHunt(TestCase):
    def setUp(self):
        thunter_dir = tempfile.mkdtemp()
        self.env = {
            "THUNTER_DIR": thunter_dir,
            "DATABASE": os.path.join(thunter_dir, "test_database.db"),
        }
        settings.THUNTER_DIR = self.env["THUNTER_DIR"]
        settings.DATABASE = self.env["DATABASE"]
        sqlite3.connect(self.env["DATABASE"])

    def tearDown(self):
        shutil.rmtree(self.env["THUNTER_DIR"])

    def test_init(self):
        thunter = TaskHunter()
        self.assertEqual(thunter.database, self.env["DATABASE"])

        thunter = TaskHunter("/database.db")
        self.assertEqual(thunter.database, "/database.db")
