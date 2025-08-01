from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestStop(CliCommandTestBaseClass):
    def test_stop(self):
        result = self.runner.invoke(thunter_cli_app, ["stop"])
        self.assertIn("Stopped working on a long task", result.output)

        result = self.runner.invoke(thunter_cli_app, ["stop"])
        self.assertIn("No current task to stop", result.output)
