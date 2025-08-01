from thunter.cli import thunter_cli_app
from thunter.tests import CliCommandTestBaseClass


class TestList(CliCommandTestBaseClass):
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
