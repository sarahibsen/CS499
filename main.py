from statisticsLogic import statistic
import numpy as np

import pandas as pd
import numpy as np
import logging

# logging for bugging / testing purposes
logging.basicConfig(filename='data_integrity.log', level=logging.ERROR)


def process_selection(df, operation):
    """
    Processes the selected data and performs the given operation.
    """
    if df.empty:
        return "Error: No data selected."

    # Detect data type
    detected_types = DataIntegrity.detect_data_type(df)

    # Ensure selected operation is applicable to the detected data type
    applicable_types = ["Discrete", "Continuous"]
    numeric_cols = [col for col in df.columns if detected_types.get(col) in applicable_types]

    if not numeric_cols:
        return "Error: No numeric data found for computation."

    # Select only numeric data
    numeric_data = df[numeric_cols].dropna().values.flatten().tolist()
    
    return f"Detected Data Types: {detected_types}, Valid for operation: {operation}"





class DataIntegrity:
    """
    Handles data validation and integrity checks before performing mathematical operations.
    """

    @staticmethod
    def validate_numeric_cells(df, selected_cells):
        """
        Ensures selected cells contain valid numeric data.
        """
        for row, col in selected_cells:
            try:
                value = df.at[row, col]
                if pd.isnull(value) or not isinstance(value, (int, float)):
                    return False  # Found invalid data
            except Exception as e:
                logging.error(f"Error accessing cell ({row}, {col}): {e}")
                return False
        return True

    @staticmethod
    def handle_missing_data(df, selected_cells, fill_value=None):
        """
        Handles missing values in selected cells by either filling them or skipping.
        """
        cleaned_values = []
        for row, col in selected_cells:
            try:
                value = df.at[row, col]
                if pd.isnull(value):
                    if fill_value is not None:
                        value = fill_value
                    else:
                        continue  # Skip NaN values
                cleaned_values.append(value)
            except Exception as e:
                logging.error(f"Error handling missing data in cell ({row}, {col}): {e}")
                continue
        return cleaned_values

    @staticmethod
    def safe_operations(operation, values):
        """
        Performs safe mathematical operations while preventing invalid calculations.
        """
        try:
            if operation == "coefficient of variation":
                return statistic.coefficientOfVariation(values)
            elif operation == "mean":
                return np.mean(values)
            elif operation == "median":
                return np.median(values)
            elif operation == "mode":
                return max(set(values), key=values.count) if values else None
            elif operation == "range":
                return max(values) - min(values) if values else None
            elif operation == "standard deviation":
                return statistic.standardDeviation(values)
            elif operation == "percentiles":
                return np.percentile(values, [25, 50, 75])
            else:
                return "Error: Unsupported operation"
        except Exception as e:
            logging.error(f"Operation error: {e}")
            return "Error: Calculation failed"


    @staticmethod
    def detect_data_type(df):
        """
        Classifies columns in the DataFrame into Discrete, Continuous, Nominal, or Ordinal.
        """
        data_types = {}
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                unique_values = df[column].nunique()
                data_types[column] = "Discrete" if unique_values < 10 else "Continuous"
            else:
                unique_values = df[column].nunique()
                data_types[column] = "Nominal" if unique_values / len(df) < 0.05 else "Ordinal"
        return data_types

class nominalStatistics:
    '''
    nominal statistics class
    '''
    def __init__(self, data):
        self.data = data
    
    def mode(self):
        return self.perform_statistics(self.data, ['mode'], 'nominal')["Mode"]
    
    def frequency(self):
        return self.perform_statistics(self.data, ['frequency'], 'nominal')["Frequency"]
    '''
    Plots associated with this data type
    '''
    def piechart(self):
        return self.perform_statistics(self.data, ['piechart'], 'nominal')["Pie Chart"]
    def bargraph(self):
        return self.perform_statistics(self.data, ['bargraph'], 'nominal')["Bar Graph"]
    

class ordinalStatistics:
    '''
    ordinal statistics class
    '''
    def __init__(self, data):
        self.data = data
    
    def proportion(self):
        return self.perform_statistics(self.data, ['proportion'], 'ordinal')["Proportion"]
    def frequency(self):
        return self.perform_statistics(self.data, ['frequency'], 'ordinal')["Frequency"]
    def percentiles(self):
        return self.perform_statistics(self.data, ['percentiles'], 'ordinal')["Percentiles"]
    
    '''
    Plots associated with this data type
    '''
    def piechart(self):
        return self.perform_statistics(self.data, ['piechart'], 'ordinal')["Pie Chart"]
    def bargraph(self):
        return self.perform_statistics(self.data, ['bargraph'], 'ordinal')["Bar Graph"]


class discreteStatistics:
    def __init__(self, data):
        self.data = data
    
    def mean(self):
        return self.perform_statistics(self.data, ['mean'], 'discrete')["Mean"]
    
    def median(self):
        return self.perform_statistics(self.data, ['median'], 'discrete')["Median"]
    def mode(self):
        return self.perform_statistics(self.data, ['mode'], 'discrete')["Mode"]
    def frequency(self):
        return self.perform_statistics(self.data, ['frequency'], 'discrete')["Frequency"]
    def range(self):
        return self.perform_statistics(self.data, ['range'], 'discrete')["Range"]
    
    '''
    plots associated with this data type
    '''
    def piechart(self):
        return self.perform_statistics(self.data, ['piechart'], 'discrete')["Pie Chart"]
    def bargraph(self):
        return self.perform_statistics(self.data, ['bargraph'], 'discrete')["Bar Graph"]
    

class continuousStatistics:
    def __init__(self, data):
        self.data = data

    
    def mean(self):
        return self.perform_statistics(self.data, ['mean'], 'continuous')["Mean"]
    
    def median(self):
        return self.perform_statistics(self.data, ['median'], 'continuous')["Median"]
    
    def mode(self):
        return self.perform_statistics(self.data, ['mode'], 'continuous')["Mode"]
    
    def standard_deviation(self):
        return self.perform_statistics(self.data, ['standard deviation'], 'continuous')["Standard Deviation"]

    def percentiles(self):
        return self.perform_statistics(self.data, ['percentiles'], 'continuous')["Percentiles"]
    
    def range(self):
        return self.perform_statistics(self.data, ['range'], 'continuous')["Range"]
    
    # check these two if they are calculated correctly
    def correlation(self, data2):
        return self.perform_statistics(self.data, ['correlation'], 'continuous')["Correlation"]
    def spearman_correlation(self, data2):
        return self.perform_statistics(self.data, ['spearman correlation'], 'continuous')["Spearman Correlation"]
    '''
    Plots associated with this data type
    '''
    def histogram(self):
        return self.perform_statistics(self.data, ['histogram'], 'continuous')["Histogram"]
    def boxplot(self):
        return self.perform_statistics(self.data, ['boxplot'], 'continuous')["Box Plot"]