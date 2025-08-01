import os
import tempfile
from unittest import TestCase

from typer.testing import CliRunner

from thunter import settings
from thunter.cli import thunter_cli_app
from thunter.tests import CliCommandTestBaseClass


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


class TestCreateCommand(CliCommandTestBaseClass):
    def test_create_task(self):
        result = self.runner.invoke(
            thunter_cli_app,
            ["create", "Test Task", "--estimate", "2", "--description", "A test task"],
        )
        self.assertIn("Test Task", result.output)
        self.assertIn("2", result.output)
        self.assertIn("A test task", result.output)

    def test_create_with_estimate_prompt(self):
        result = self.runner.invoke(
            thunter_cli_app,
            ["create", "Test Task with Prompt"],
            input="3\n",
        )
        self.assertIn("Test Task with Prompt", result.output)
        self.assertIn("3", result.output)


class TestListCommand(CliCommandTestBaseClass):
    def test_list_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls"])
        self.assertIn("Current", result.output)
        self.assertIn("In Progress", result.output)
        self.assertIn("TODO", result.output)
        self.assertNotIn("Finished", result.output)

    def test_list_all_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--all"])
        self.assertIn("Current", result.output)
        self.assertIn("In Progress", result.output)
        self.assertIn("TODO", result.output)
        self.assertIn("Finished", result.output)

    def test_list_finished_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--finished"])
        self.assertNotIn("Current", result.output)
        self.assertNotIn("In Progress", result.output)
        self.assertNotIn("TODO", result.output)
        self.assertIn("Finished", result.output)

    def test_list_todo_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--todo"])
        self.assertNotIn("Current", result.output)
        self.assertNotIn("In Progress", result.output)
        self.assertIn("TODO", result.output)
        self.assertNotIn("Finished", result.output)

    def test_list_open_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--open"])
        self.assertIn("Current", result.output)
        self.assertIn("In Progress", result.output)
        self.assertIn("TODO", result.output)
        self.assertNotIn("Finished", result.output)

    def test_list_started_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--started"])
        self.assertIn("Current", result.output)
        self.assertIn("In Progress", result.output)
        self.assertNotIn("TODO", result.output)
        self.assertNotIn("Finished", result.output)

    def test_list_current_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--current"])
        self.assertIn("Current", result.output)
        self.assertNotIn("In Progress", result.output)
        self.assertNotIn("TODO", result.output)
        self.assertNotIn("Finished", result.output)

    def test_list_in_progress_tasks(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--in-progress"])
        self.assertNotIn("Current", result.output)
        self.assertIn("In Progress", result.output)
        self.assertNotIn("TODO", result.output)
        self.assertNotIn("Finished", result.output)

    def test_list_starts_with(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--starts-with", "a "])
        self.assertNotIn("another great test task", result.output)
        self.assertIn("a test task", result.output)
        self.assertIn("a long task", result.output)
        self.assertNotIn("a finished task", result.output)

    def test_list_contains(self):
        result = self.runner.invoke(thunter_cli_app, ["ls", "--contains", "test"])
        self.assertIn("another great test task", result.output)
        self.assertIn("a test task", result.output)
        self.assertNotIn("a finished task", result.output)
        self.assertNotIn("a long task", result.output)


class TestShowCommand(CliCommandTestBaseClass):
    def test_show_task(self):
        result = self.runner.invoke(thunter_cli_app, ["show"])
        self.assertIn("a long task", result.output)
        self.assertIn("Current", result.output)

        result = self.runner.invoke(thunter_cli_app, ["show", "a test task"])
        self.assertIn("a test task", result.output)

        result = self.runner.invoke(thunter_cli_app, ["show", "4"])
        self.assertIn("a finished task", result.output)

    def test_show_nonexistent_task(self):
        result = self.runner.invoke(thunter_cli_app, ["show", "999"])
        self.assertIn("Could not find task for identifier: 999", str(result.exception))
        self.assertGreater(result.exit_code, 0)

        self.thunter.stop_current_task()
        result = self.runner.invoke(thunter_cli_app, ["show"])
        self.assertIn("No Current task found.", str(result.exception))
        self.assertGreater(result.exit_code, 0)


class TestWorkonCommand(CliCommandTestBaseClass):
    def test_workon_task(self):
        result = self.runner.invoke(thunter_cli_app, ["show"])
        self.assertIn("a long task", result.output)
        self.assertNotIn("a test task", result.output)

        self.runner.invoke(thunter_cli_app, ["workon", "a test task"])
        result = self.runner.invoke(thunter_cli_app, ["show"])
        self.assertNotIn("a long task", result.output)
        self.assertIn("a test task", result.output)

    def test_workon_nonexistent_task(self):
        result = self.runner.invoke(thunter_cli_app, ["workon", "999"])
        self.assertIn("Could not find task for identifier: 999", str(result.exception))
        self.assertGreater(result.exit_code, 0)
