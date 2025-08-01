from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestCreate(CliCommandTestBaseClass):
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
