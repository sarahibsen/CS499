import unittest
from unittest.mock import MagicMock
import tkinter as tk
from GUI import DashboardPage

class TestDashboardPage(unittest.TestCase):
    def setUp(self):
        # Create a root Tkinter instance
        self.root = tk.Tk()
        self.controller = MagicMock()  # Mock the controller
        self.dashboard_page = DashboardPage(self.root, self.controller)

    def tearDown(self):
        # Destroy the Tkinter instance after each test
        self.root.destroy()

    def test_display_results(self):
        # Mock results dictionary
        results = {
            "Stat1": {"Header1": 10, "Header2": 20},
            "Stat2": {"Header2": 30, "Header3": 40}
        }

        # Call the method
        self.dashboard_page.display_results(results)

        # Check if headers are updated correctly
        expected_headers = ["Header1", "Header2", "Header3"]
        self.assertEqual(self.dashboard_page.result_headers, expected_headers)

        # Check if rows are updated correctly
        expected_rows = {
            1: [10, 20, ""],  # Row for Stat1
            2: ["", 30, 40]   # Row for Stat2
        }
        self.assertEqual(self.dashboard_page.result_rows, expected_rows)

        # Verify that the TableView is updated with the correct headers and data
        table_mock = self.dashboard_page.result_rows
        self.assertIsNotNone(table_mock)

if __name__ == "__main__":
    unittest.main()