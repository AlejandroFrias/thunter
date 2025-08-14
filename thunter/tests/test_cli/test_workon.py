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
            thunter_cli_app, ["workon", "a brand new task", "--create"], input="1\n"
        )
        self.assertTrue(re.search("a brand new task.*Current", result.output))

    def test_workon_nonexistent_task_by_id(self):
        result = self.runner.invoke(thunter_cli_app, ["workon", "999"])
        self.assertIn("Could not find task for identifier: 999", str(result.exception))
        self.assertGreater(result.exit_code, 0)

    def test_workon_nonexistent_task_by_name(self):
        result = self.runner.invoke(thunter_cli_app, ["workon", "a nonexistent task"])
        self.assertIn(
            "Could not find task for identifier: a nonexistent task",
            str(result.exception),
        )
        self.assertGreater(result.exit_code, 0)

    def test_workon_partial_task_id_match(self):
        result = self.runner.invoke(thunter_cli_app, ["workon", "another"])
        self.assertIn("another great test task", result.output)
        self.assertNotIn("a long task", result.output)

    def test_workon_last_modified_task(self):
        result = self.runner.invoke(thunter_cli_app, ["stop"])
        self.assertIn("a long task", result.output)

        result = self.runner.invoke(thunter_cli_app, ["workon"])
        self.assertIn("a long task", result.output)

    def test_no_tasks_to_workon(self):
        self.runner.invoke(thunter_cli_app, ["finish", "1"])
        self.runner.invoke(thunter_cli_app, ["finish", "2"])
        self.runner.invoke(thunter_cli_app, ["finish", "5"])
        self.runner.invoke(thunter_cli_app, ["finish", "6"])
        self.runner.invoke(thunter_cli_app, ["finish", "7"])

        result = self.runner.invoke(thunter_cli_app, ["workon"])
        self.assertGreater(result.exit_code, 0)
        self.assertIn("No task found", str(result.exception))

    def test_workon_create_keeps_prompting_for_estimate(self):
        result = self.runner.invoke(
            thunter_cli_app,
            ["workon", "a brand new task", "--create"],
            input="0\n2\n",
        )
        self.assertTrue(re.search("Estimate must be at least 1 hour", result.output))
        self.assertTrue(re.search("a brand new task.*Current", result.output))
        self.assertTrue(re.search("a brand new task.*2 hrs.*Current", result.output))
