# Refactored Controller as a lightweight Component
import pandas as pd
from Table import TableController
from statisticsLogic import *
from main import DataIntegrity, nominalStatistics, ordinalStatistics, discreteStatistics, continuousStatistics

class Controller:
    """
    A lightweight component class responsible for handling statistical operations
    without storing data.
    """

    @staticmethod
    def load_data_from_table(table_controller):
        """
        Fetches selected data from the table via TableController.

        Args:
            table_controller (TableController): The table controller instance.

        Returns:
            pd.DataFrame: The selected data as a DataFrame.
        """
        return table_controller.get_table_selection()

    @staticmethod
    def validate_data(data_frame):
        """
        Checks if the selected data contains only numeric values.

        Args:
            data_frame (pd.DataFrame): The data to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        if data_frame is None or data_frame.empty:
            return False

        selected_cells = [(r, c) for r in range(data_frame.shape[0]) for c in range(data_frame.shape[1])]
        return DataIntegrity.validate_numeric_cells(data_frame, selected_cells)

    @staticmethod
    def detect_data_type(data_frame):
        """
        Detects the type of data in the DataFrame.

        Args:
            data_frame (pd.DataFrame): The data to analyze.

        Returns:
            dict: Column-wise data type mapping.
        """
        return DataIntegrity.detect_data_type(data_frame) if data_frame is not None else None

    @staticmethod
    def perform_statistics(data_frame, selected_measures, data_type):
        """
        Performs statistical computations based on the selected data type and measures.

        Args:
            data_frame (pd.DataFrame): The data to analyze.
            selected_measures (list): List of statistical measures.
            data_type (str): Data classification (Nominal, Ordinal, Discrete, Continuous).

        Returns:
            dict: Computed statistical results.
        """
        if data_frame is None or data_frame.empty:
            return None

        # Select the appropriate statistics class
        statistics_classes = {
            "Nominal": nominalStatistics,
            "Ordinal": ordinalStatistics,
            "Discrete": discreteStatistics,
            "Continuous": continuousStatistics,
        }

        if data_type not in statistics_classes:
            return None

        logic = statistics_classes[data_type](data_frame)

        # Compute requested measures
        results = {}
        #TODO : add more measures
        measure_functions = {
            "Mean": logic.mean if hasattr(logic, "mean") else None,
            "Median": logic.median if hasattr(logic, "median") else None,
            "Mode": logic.mode if hasattr(logic, "mode") else None,
            "Standard Deviation": logic.standard_deviation if hasattr(logic, "standard_deviation") else None,
            "Variance": logic.variance if hasattr(logic, "variance") else None,
            "Range": logic.range if hasattr(logic, "range") else None,
            "Frequency": logic.frequency if hasattr(logic, "frequency") else None,
            "Percentiles": logic.percentiles if hasattr(logic, "percentiles") else None,
            

        }

        for measure in selected_measures:
            if measure in measure_functions and measure_functions[measure]:
                results[measure] = measure_functions[measure]()
            else:
                print(f"Measure '{measure}' not supported for data type '{data_type}'")

        return results

    @staticmethod
    def export_results(results, filename="stats_results.csv"):
        """
        Exports statistical results to a CSV file.

        Args:
            results (dict): The computed statistical results.
            filename (str): The filename for the output CSV.
        """
        if not results:
            print("No results to export.")
            return

        df = pd.DataFrame(list(results.items()), columns=["Measure", "Value"])
        df.to_csv(filename, index=False)
        print(f"Results exported to {filename}")
