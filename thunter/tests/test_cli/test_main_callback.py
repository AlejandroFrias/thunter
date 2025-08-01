import os
import tempfile
from unittest import TestCase

from typer.testing import CliRunner

from thunter import settings
from thunter.cli import thunter_cli_app


class TestMainCallback(TestCase):
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(thunter_cli_app, ["--help"])
        self.assertIn("Usage: thunter", result.output)
        self.assertIn("THunter - your task hunter", result.output)

    def test_init_called_by_default(self):
        with tempfile.TemporaryDirectory() as thunter_dir:
            settings.THUNTER_DIR = thunter_dir
            settings.DATABASE = os.path.join(thunter_dir, "uninitialized.db")
            runner = CliRunner()
            result = runner.invoke(thunter_cli_app, ["ls"])
            self.assertIn("Initializing THunter...", result.output)

            self.assertTrue(os.path.exists(thunter_dir + "/uninitialized.db"))

    def test_thunter_silent(self):
        with tempfile.TemporaryDirectory() as thunter_dir:
            settings.THUNTER_DIR = thunter_dir
            settings.DATABASE = os.path.join(thunter_dir, "uninitialized.db")
            runner = CliRunner()
            result = runner.invoke(
                thunter_cli_app,
                ["--silent", "create", "Silent Task", "--estimate", "1"],
            )
            self.assertEqual("", result.output)
