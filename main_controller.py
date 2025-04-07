# Refactored Controller as a lightweight Component
import pandas as pd
from Table import TableController
from statisticsLogic import statistic
from main import DataIntegrity, nominalStatistics, ordinalStatistics, discreteStatistics, continuousStatistics
import datetime
from tkinter import filedialog
import numpy as np

# adding warning diflection from pandas 
pd.set_option('future.no_silent_downcasting', True)


class Controller:
    """
    A lightweight component class responsible for handling statistical operations
    without storing data.
    """ 

    @staticmethod
    def load_data_from_table(table_controller):
        if not hasattr(table_controller, 'get_table_selection'):
            print("Error: Table instance is not initialized.")
            return pd.DataFrame()

        data = table_controller.get_table_selection()
        print(f"Loaded Data:\n{data}")

        # Ensure proper data types
        for col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            #data.fillna(0, inplace=True)  # for missing data
            #data = data.fillna(0).infer_objects(copy=False)

        # Filter non-zero data only
        data = data[(data != 0).any(axis=1)]
        data = data.dropna(axis=1, how='all')  # Drop columns with all NaN values

        print(f"Data loaded into Controller:\n{data}")
        return data

    @staticmethod
    def load_entire_table(table_controller):
        """ Retrieves data in table w/o converting it to numeric """
        if not hasattr(table_controller, 'get_table_selection'):
            print("Error: Table instance is not initialized.")
            return pd.DataFrame()

        data = table_controller.get_entire_table()
        print(f"Loaded Data:\n{data}")

        # Drop columns with all NaN values
        data = data.dropna(axis=1, how='all')

        print(f"Data loaded into Controller:\n{data}")
        return data

    @staticmethod
    def validate_data(data_frame):
        if data_frame is None or data_frame.empty:
            print("Data validation failed: Empty DataFrame")
            return False

        numeric_cols = data_frame.select_dtypes(include='number').columns
        if numeric_cols.empty:
            print("Data validation failed: No numeric columns found.")
            return False

        print("Data validation successful!")
        return True


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
    def perform_statistics(data_frame, selected_measures, data_type, variance_type = None):
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
        stat_instance = statistic(data_frame)


        # Compute requested measures
        results = {}
        #TODO : add more measures
        measure_functions = {
            "Mean": stat_instance.mean,
            "Median": stat_instance.median,
            "Mode": stat_instance.mode,
            "Standard Deviation": stat_instance.standardDeviation,
            "Variance": lambda: stat_instance.variance(variance_type),
            "Coefficient of Variation": stat_instance.coefficientOfVariation,
            "Percentiles": stat_instance.percentiles,
            "Probability Distribution": stat_instance.probabilityDistribution,
            "Binomial Distribution": lambda: stat_instance.binomialDistribution(
                data_frame.select_dtypes(include='number').values.flatten()  # Dynamic sample size
            ),
            "Least Square Line": stat_instance.leastSquareLine,
            "Chi Square": stat_instance.chiSquared, 
            "Correlation": stat_instance.correlationCoefficient,
            "Sign Test": stat_instance.signTest,
            "Rank Sum": stat_instance.rankSum,
            "Spearman Correlation": stat_instance.spearmanRankCorrelation,
            #"Frequency": stat_instance.frequency,

        }
        # allow for the possibility of users to input their own measures
        
        for measure in selected_measures:
            if measure in measure_functions:
                try:
                    results[measure] = measure_functions[measure]()
                except Exception as e:
                    print(f"Error calculating {measure}: {e}")
            else:
                print(f"Measure '{measure}' not supported for data type '{data_type}'")

        return results

    @staticmethod
    def export_results(results, filename=None):
        """
        Enhanced export method to:
        - Add a timestamp to the filename
        - Provide detailed descriptions of the statistical analysis performed
        - Include column/row selection details for better context
        """
        if not results:
            print("No results to export.")
            return

        # detailed results with column/row details
        detailed_results = []
        for measure, value in results.items():
            # Check if value is iterable (like a list) or a single value (like float/int)
            if isinstance(value, (list, np.ndarray)):
                detail_text = f"Analysis performed on {len(value)} selected entries"
            else:
                detail_text = "Single value result (not iterable)"
            
            detailed_results.append({
                "Measure": measure,
                "Value": value,
                "Details": detail_text
            })

        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = filename or f"stats_results_{timestamp}.csv"

        df = pd.DataFrame(detailed_results)
        df.to_csv(filename, index=False)
        print(f"Results exported to {filename}")

    @staticmethod
    def get_data_type_classes():
        """
        Instead of statically defining the data types in the GUI drop down, we can
        dynamically generate the data types based on the available classes.
        """
        return {
            "Nominal": nominalStatistics,
            "Ordinal": ordinalStatistics,
            "Discrete": discreteStatistics,
            "Continuous": continuousStatistics,
        }
    @staticmethod
    def measures_for_data_type(data_type):
        """
        """
        classes = {
            "Nominal": nominalStatistics,
            "Ordinal": ordinalStatistics,
            "Discrete": discreteStatistics,
            "Continuous": continuousStatistics
        }

        if data_type not in classes:
            return {}
        class_obj = classes[data_type]

        raw_methods = [
            func for func in dir(class_obj)
            if not func.startswith("_") and callable(getattr(class_obj, func))
        ]

        
        display_map = {}
        for method in raw_methods:
            # Convert camelCase or snake_case to display-friendly version
            display_name = (
                ''.join([' ' + c if c.isupper() else c for c in method])
                .replace('_', ' ')
                .title()
                .strip()
            )
            display_map[display_name] = method

        return display_map

    @staticmethod
    def plots_for_measure(measure):
        """Return appropriate plots based on the selected statistical measure."""
        if measure in ["Mean", "Median", "Mode", "Standard Deviation", "Coefficient of Variation", "Percentiles"]:
            return ["Horizontal Bar Chart", "Vertical Bar Chart", "Pie Chart", "Normal Distribution Curve"]

        elif measure in ["Probability Distribution", "Binomial Distribution", "Least Square Line"]:
            return ["Scatter Plot", "Normal Distribution Curve"]

        elif measure in ["Chi Square", "Sign Test", "Rank Sum"]:
            return ["Horizontal Bar Chart", "Vertical Bar Chart"]

        elif measure in ["Correlation", "Spearman Correlation"]:
            return ["Scatter Plot"]

        else:
            return ["Horizontal Bar Chart", "Vertical Bar Chart"]  # Safe fallback
