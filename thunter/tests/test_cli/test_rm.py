from thunter.tests import CliCommandTestBaseClass
from thunter.cli import thunter_cli_app


class TestRm(CliCommandTestBaseClass):
    def test_rm_unsure(self):
        result = self.runner.invoke(
            thunter_cli_app, ["rm", "a finished task"], input="n\n"
        )
        self.assertIn("Didn't remove a finished task.", result.output)

    def test_rm_sure(self):
        result = self.runner.invoke(
            thunter_cli_app, ["rm", "a finished task"], input="y\n"
        )
        self.assertIn("Removed a finished task!", result.output)

    def test_rm_force(self):
        result = self.runner.invoke(
            thunter_cli_app, ["rm", "a finished task", "--force"]
        )
        self.assertIn("Removed a finished task!", result.output)
