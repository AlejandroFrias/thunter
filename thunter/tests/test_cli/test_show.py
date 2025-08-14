from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestShow(CliCommandTestBaseClass):
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

    def test_show_most_recent_task(self):
        self.thunter.stop_current_task()
        result = self.runner.invoke(thunter_cli_app, ["show"])
        self.assertIn("a long task", str(result.output))
