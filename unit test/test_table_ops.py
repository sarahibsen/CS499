import unittest
import pandas as pd
from Table import TableController, TableView
import tkinter as tk
from tkinter import Tk


class TestTableSelection(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.table_controller = TableController(self.root)

        # Sample Data
        self.sample_data = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8],
            'C': [9, 10, 11, 12]
        })
        
    def test_get_table_selection(self):
        # Create a valid table instance before calling update_table
        table_frame = tk.Frame(self.root)
        table = TableView(table_frame)
        table_instance = table.sheet
        self.table_controller.update_table(table_instance, headers=self.sample_data.columns.tolist(), data=self.sample_data.values.tolist())
        
        selected_data = self.table_controller.get_table_selection()
        
        # Assert data is correctly retrieved
        self.assertIsInstance(selected_data, pd.DataFrame)
        self.assertEqual(selected_data.shape, self.sample_data.shape)


    def tearDown(self):
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()
