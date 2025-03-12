# Refactored Controller as a lightweight Component
import pandas as pd
from Table import TableController
from statisticsLogic import statistic
from main import DataIntegrity, nominalStatistics, ordinalStatistics, discreteStatistics, continuousStatistics

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

        # Ensure proper data types
        for col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='ignore')

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
        stat_instance = statistic(data_frame.select_dtypes(include='number').values) # statistic instance 


        # Compute requested measures
        results = {}
        #TODO : add more measures
        measure_functions = {
            "Mean": stat_instance.mean,
            "Median": stat_instance.median,
            "Mode": stat_instance.mode,
            "Standard Deviation": stat_instance.standardDeviation,
            "Variance": stat_instance.variance,
            "Coefficient of Variation": stat_instance.coefficientOfVariation,
            "Percentile": stat_instance.percentiles,
            "Probability Distribution": stat_instance.probabilityDistribution,
            "Binomial Distribution": stat_instance.binomialDistribution,
            "Least Square Line": stat_instance.leastSquareLine,
            "Chi-Square Test": stat_instance.chiSquared, 
            "Correlation Coefficient": stat_instance.correlationCoefficient,
            "Significance Test": stat_instance.significanceTest,
            "Rank Sum": stat_instance.rankSum,
            "Spearman Coefficient": stat_instance.spearmanRankCorrelation,

        }
        # allow for the possibility of users to input their own measures
        
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
