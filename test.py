from GUI import *
from statisticsLogic import *
from customTable import *


'''
Attaching the backend and frontend. 
Statistical Analyzer is a GUI application that allows users to perform statistical analysis on datasets.
'''


def upload_data(self):
    """
    Handles CSV data upload and display the custom table.
    """
    print("Upload data button clicked.")

    # initialize and open the table interface 
    table_app = CustomTable()
    
    data = table_app.table.model.df.select_dtypes(include=[np.number]).values.flatten()

    # pass numerical data to the statistics logic
    self.run_statistics(data)

def run_statistics(self, data):
    """
    run statistical functions on the provided data and display results
    """
    stats = statistic(data)
    print("Mean: ", stats.mean())
    print("Variance: ", stats.variance())
    print("Standard Deviation: ", stats.std_dev())

def button_1_placeholder(self):
    """
    Display selection-based statistics results on button click.
    """
    # Collect data, assume data is shared between pages via controller object
    data = self.controller.shared_data.get("numeric_data", [])

    if len(data) == 0:
        print("No data available. Please upload data first.")
        return

    # Run selected statistic (as an example)
    stats = statistic(data)
    print("Standard Deviation:", stats.standardDeviation())
