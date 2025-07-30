from unittest import TestCase

from typer.testing import CliRunner

from thunter import settings
from thunter.cli import thunter_cli_app
from thunter.task_hunter import TaskHunter
from thunter.tests import setUpTestDatabase, tearDownTestDatabase


class TestCli(TestCase):

    def setUp(self):
        self.env = setUpTestDatabase()
        self.thunter = TaskHunter()
        self.runner = CliRunner()

    def tearDown(self):
        """Remove the temporary environment and database after tests."""
        tearDownTestDatabase(self.env)

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

    def test_thunter_silent(self):
        settings.THUNTER_SILENT = "1"
        result = self.runner.invoke(
            thunter_cli_app,
            ["create", "Silent Task", "--estimate", "1"],
        )
        self.assertEqual("", result.output)
