import re
from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestWorkon(CliCommandTestBaseClass):
    def test_workon_task(self):
        result = self.runner.invoke(thunter_cli_app, ["show"])
        self.assertIn("a long task", result.output)
        self.assertNotIn("a test task", result.output)

        self.runner.invoke(thunter_cli_app, ["workon", "a test task"])
        result = self.runner.invoke(thunter_cli_app, ["show"])
        self.assertNotIn("a long task", result.output)
        self.assertIn("a test task", result.output)

    def test_workon_and_create_task(self):
        result = self.runner.invoke(
            thunter_cli_app, ["workon", "a brand new task", "--create"]
        )
        self.assertTrue(re.search("a brand new task.*Current", result.output))

    def test_workon_nonexistent_task(self):
        result = self.runner.invoke(thunter_cli_app, ["workon", "999"])
        self.assertIn("Could not find task for identifier: 999", str(result.exception))
        self.assertGreater(result.exit_code, 0)
