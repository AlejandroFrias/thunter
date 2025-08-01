from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestFinish(CliCommandTestBaseClass):
    def test_finish_current_task(self):
        result = self.runner.invoke(thunter_cli_app, ["finish"])
        self.assertIn("Finished a long task", result.output)

        result = self.runner.invoke(thunter_cli_app, ["show", "a finished task"])
        self.assertIn("Finished", result.output)

    def test_finish_specific_test(self):
        result = self.runner.invoke(thunter_cli_app, ["finish", "6"])
        self.assertIn("Finished identically named task", result.output)

        result = self.runner.invoke(thunter_cli_app, ["show", "6"])
        self.assertIn("Finished", result.output)

    def test_finish_no_task_found(self):
        result = self.runner.invoke(thunter_cli_app, ["finish", "9999"])
        self.assertIn("Could not find task for identifier: 9999", str(result.exception))
        self.assertGreater(result.exit_code, 0)
