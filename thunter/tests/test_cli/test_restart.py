import re
from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestRestart(CliCommandTestBaseClass):
    def test_restart_finished_task(self):
        result = self.runner.invoke(thunter_cli_app, ["restart", "a finished task"])
        self.assertTrue(re.search(r"a finished task.*Current", result.output))

    def test_restart_no_task(self):
        result = self.runner.invoke(thunter_cli_app, ["restart", "a long task"])
        self.assertIn(
            "Could not find task for identifier: a long task", str(result.exception)
        )
        self.assertGreater(result.exit_code, 0)
