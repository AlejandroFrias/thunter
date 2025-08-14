from unittest import TestCase

import pandas as pd

from thunter.analyzer import TaskAnalyzer
from thunter.tests import setUpTestDatabase, tearDownTestDatabase


class TestTaskAnalyzer(TestCase):
    def setUp(self):
        self.env = setUpTestDatabase()
        self.analyzer = TaskAnalyzer()

    def tearDown(self):
        """Remove the temporary environment and database after tests."""
        tearDownTestDatabase(self.env)

    def test_fetch_data_df(self):
        df = self.analyzer.fetch_data_df()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("estimate", df.columns)
        self.assertIn("is_start", df.columns)
        self.assertIn("time", df.columns)
        self.assertEqual(df["estimate"].dtype, "Int32")
        self.assertEqual(df["is_start"].dtype, "boolean")
        self.assertEqual(df["time"].dtype, "Int64")
