from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestEstimate(CliCommandTestBaseClass):
    def test_estimate_current_task(self):
        result = self.runner.invoke(thunter_cli_app, ["estimate", "7"])
        self.assertIn("a long task estimated to take 7 hrs.", result.output)

    def test_estimate_no_current_task(self):
        self.runner.invoke(thunter_cli_app, ["stop"])
        result = self.runner.invoke(thunter_cli_app, ["estimate", "7"])
        self.assertIn("No current task found to estimate.", str(result.exception))
        self.assertGreater(result.exit_code, 0)

    def test_estimate_specific_tas(self):
        result = self.runner.invoke(
            thunter_cli_app, ["estimate", "--task-identifier", "a test task", "7"]
        )
        self.assertIn("a test task estimated to take 7 hrs.", result.output)
