# Refactored Controller as a lightweight Component
import pandas as pd

import statisticsLogic
from Table import TableController, TableModel
from statisticsLogic import statistic
import datetime
from tkinter import filedialog
import numpy as np
from tkinter import messagebox
from data_utils import clean_numeric_data

# adding warning diflection from pandas 
pd.set_option('future.no_silent_downcasting', True)


class Controller:
    """
    A lightweight component class responsible for handling statistical operations
    without storing data.
    """

    last_stat_instance = None

    def __init__(self):
        self.binomial_params = {'n': None, 'p': None}

    @staticmethod
    def load_data_from_table(table_controller):
        if not hasattr(table_controller, 'get_table_selection'):
            print("Error: Table instance is not initialized.")
            return pd.DataFrame()

        data = table_controller.get_table_selection()
        #print(f"Loaded Data:\n{data}")

        # Ensure proper data types
        for col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            #data.fillna(0, inplace=True)  # for missing data
            #data = data.fillna(0).infer_objects(copy=False)

        # Filter non-zero data only
        data = data[(data != 0).any(axis=1)]
        data = data.dropna(axis=1, how='all')  # Drop columns with all NaN values
        # filter if there are mixed data types 
        data = data.select_dtypes(include=[np.number]).dropna()

        return data

    @staticmethod
    def load_entire_table(table_controller):
        """ Retrieves data in table w/o converting it to numeric """
        if not hasattr(table_controller, 'get_table_selection'):
            print("Error: Table instance is not initialized.")
            return pd.DataFrame()

        data = table_controller.get_entire_table()
        #print(f"Loaded Data:\n{data}")

        # Drop columns with all NaN values
        data = data.dropna(axis=1, how='all')

        #print(f"Data loaded into Controller:\n{data}")
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
    def perform_statistics(data_frame, selected_measures, data_type, variance_type=None, extra_params=None):
        if data_frame is None or data_frame.empty:
            return None

        stat_instance = statistic(data_frame)
        Controller.last_stat_instance = stat_instance

        measure_functions = {
            "Mean": stat_instance.mean,
            "Median": stat_instance.median,
            "Mode": stat_instance.mode,
            "Standard Deviation": stat_instance.standardDeviation,
            "Variance": lambda: stat_instance.variance(variance_type),
            "Coefficient Of Variation": stat_instance.coefficientOfVariation,
            "Percentiles": stat_instance.percentiles,
            "Probability Distribution": stat_instance.probabilityDistribution,
            "Binomial Distribution": lambda: stat_instance.binomialDistribution(
                data_frame.select_dtypes(include='number').values.flatten(),
                n=extra_params.get("n"),
                p=extra_params.get("p")
            ) if extra_params else None,
            "Least Square Line": stat_instance.leastSquareLine,
            "Chi Square": stat_instance.chiSquared,
            "Correlation": stat_instance.correlationCoefficient,
            "Sign Test": stat_instance.signTest,
            "Rank Sum": stat_instance.rankSum,
            "Spearman Rank Correlation": stat_instance.spearmanRankCorrelation,
        }

        results = {}
        for measure in selected_measures:
            if measure not in measure_functions:
                print(f"Measure '{measure}' not supported")
                continue
            try:
                results[measure] = measure_functions[measure]()
            except Exception as e:
                print(f"Error calculating {measure}: {e}")

        return results
    
    @staticmethod
    def calculate_statistics(data_frame, selected_measures, extra_params=None):
        if data_frame.empty:
            return {}, selected_measures

        data_frame = clean_numeric_data(data_frame)
        print("After cleaning:")
        print(data_frame)

        all_measures = list(statistic.registered_measures.keys())
        compatible = all_measures + selected_measures
        incompatible = [m for m in selected_measures if m not in compatible]
        valid = [m for m in selected_measures if m in compatible]

        stat_instance = statistic(data_frame)
        Controller.last_stat_instance = stat_instance

        results = {}
        for m in valid:
            try:
                func = statistic.registered_measures.get(m)
                options = extra_params.get(m) if extra_params else None

                if m == "Binomial Distribution":
                    n = extra_params.get("n", 10) if extra_params else 10
                    p = extra_params.get("p", 0.5) if extra_params else 0.5
                    result = func(stat_instance, n=n, p=p)

                elif m == "Percentiles":
                    if options:
                        # Check if custom numeric values were passed
                        if all(isinstance(opt, str) and opt.endswith("th Percentile") for opt in options):
                            # Extract raw values from "90th Percentile" strings
                            raw_values = []
                            for opt in options:
                                try:
                                    val = int(opt.replace("th Percentile", "").strip())
                                    raw_values.append(val)
                                except:
                                    continue
                            result = func(stat_instance, option=raw_values)
                        else:
                            # Use predefined labels or lists
                            result = None
                            all_percentile_results = []
                            for opt in options:
                                partial = func(stat_instance, option=opt)
                                if partial:
                                    all_percentile_results.append(partial)
                            result = {all_percentile_results}
                    else:
                        result = func(stat_instance)

                elif m == "Probability Distribution":
                    result = None
                    if options:
                        # If multiple distribution types were somehow selected, take the first (or handle them all if needed)
                        result = func(stat_instance, option=options[0] if isinstance(options, list) else options)
                    else:
                        # No option selected, so use the default
                        result = func(stat_instance, option=None)
                elif m == "Chi Square":
                    col_info = extra_params.get(m) if extra_params else {}
                    expected_col = col_info.get("expected") if isinstance(col_info, dict) else None
                    observed_col = col_info.get("observed") if isinstance(col_info, dict) else None
                    result = func(stat_instance, expected=expected_col, observed=observed_col)

                elif m == "Variance":
                    # Auto-pick based on sample size if not provided
                    selected_option = None

                    if options and isinstance(options, list) and options:
                        selected_option = options[0]  # User explicitly chose
                    else:
                        row_count = len(data_frame)
                        selected_option = "Population" if row_count > 30 else "Sample"

                    result = func(stat_instance, variance_type=selected_option)

                elif m == "Sign Test":
                    if options and isinstance(options, list):
                        result = func(stat_instance, option=options)
                    else:
                        result = func(stat_instance, option="two-sided")

                else:
                    # For all other statistics that don't need specifications
                    result = func(stat_instance)

                if result is not None:
                    results[m] = result if isinstance(result, dict) else {m: result}
                else:
                    print(f"{m} was not computed due to an error or invalid data.")


            except Exception as e:
                print(f"Error computing {m}: {e}")

        return results, incompatible

    @staticmethod
    def export_results(results, filename=None):
        if not results:
            print("No results to export.")
            return

        detailed_results = []
        for measure, value in results.items():
            detail = f"Analysis performed on {len(value)} selected entries" if isinstance(value, (list, np.ndarray)) else "Single value result"
            detailed_results.append({"Measure": measure, "Value": value, "Details": detail})

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = filename or f"stats_results_{timestamp}.txt"

        pd.DataFrame(detailed_results).to_csv(filename, index=False)
        print(f"Results exported to {filename}")

    @staticmethod
    def measures_for_data_type(data_type):
        classes = Controller.get_data_type_classes()
        if data_type not in classes:
            return {}

        methods = [
            func for func in dir(classes[data_type])
            if not func.startswith("_") and callable(getattr(classes[data_type], func))
        ]

        display_map = {
            ''.join([' ' + c if c.isupper() else c for c in method]).replace('_', ' ').title().strip(): method
            for method in methods
        }

        return display_map

    @staticmethod
    def plots_for_measure(measure):
        if isinstance(measure, list):
            # Combine all unique valid plots for the list of measures
            plots = set()
            for m in measure:
                plots.update(Controller.plots_for_measure(m))
            return list(plots)

            # Handle single measure
        if measure not in statistic.registered_measures:
            return ["Vertical Bar Chart", "Horizontal Bar Chart"]
        if measure in ["Chi Square", "Sign Test", "Rank Sum"]:
            return ["Vertical Bar Chart", "Horizontal Bar Chart"]
        elif measure in ["Mean", "Median", "Mode"]:
            return ["Vertical Bar Chart", "Horizontal Bar Chart", "Pie Chart"]
        elif measure in ["Probability Distribution", "Standard Deviation", "Variance", "Coefficient of Variation", "Binomial Distribution"]:
            return ["Normal Distribution Curve"]
        elif measure == "Percentiles":
            return ["Normal Distribution Curve", "Vertical Bar Chart", "Horizontal Bar Chart"]
        elif measure in ["Spearman Rank Correlation", "Least Square Line", "Correlation Coefficient"]:
            return ["Scatter Plot"]
        return ["Vertical Bar Chart", "Horizontal Bar Chart"]

    @staticmethod
    def measure_supports_grouping(measure):
        """
        Returns "No grouping" if the measure cannot be graphed with grouping,
        "Must group" if the measure can only be graphed with grouping,
        and "Both" if the measure can be grouped or not grouped.
        Custom measures default to "No grouping".
        """

        # If it's a custom measure (registered but not listed in requirements)
        if measure in statistic.registered_measures and measure not in statistic.measure_requirements:
            return "No grouping"

        if measure in ["Standard Deviation", "Variance", "Percentiles", "Binomial Distribution",
                       "Probability Distribution", "Coefficient of Variation"]:
            return "No grouping"
        elif measure in ["Chi Square", "Least Square Line", "Correlation Coefficient",
                         "Rank Sum", "Spearman Rank Correlation", "Mode", "Sign Test"]:
            return "Must group"
        return "Both"

    def set_binomial_params(self, n, p):
        """Store the binomial parameters"""
        self.binomial_params = {'n': n, 'p': p}
        print(self.binomial_params)

    def get_last_binomial_params(self):
        """Returns the last used binomial parameters (n, p)"""
        print("get")
        print(self.binomial_params)
        return self.binomial_params.get('n'), self.binomial_params.get('p')


    @staticmethod
    def get_last_selected_percentiles():
        instance = Controller.last_stat_instance
        if instance and hasattr(instance, 'selected_percentiles'):
            return instance.selected_percentile_label, instance.selected_percentiles
        return None, None

    @staticmethod
    def get_compatible_measures(df, selected_columns=None):

        type_map = TableModel().detect_data_type(df)
        present_types = set(type_map.values())

        if selected_columns:
            numeric_df = df[selected_columns].select_dtypes(include=[np.number]).dropna()
        else:
            numeric_df = df.select_dtypes(include=[np.number]).dropna()
        num_columns = numeric_df.shape[1]
        num_rows = numeric_df.shape[0]

        compatible = []

        for measure, rules in statistic.measure_requirements.items():
            # Skip if no columns match required types
            required_types = set(rules["types"])
            if not required_types.intersection(present_types):
                continue

            # CHI-SQUARE SPECIFIC CHECKS
            if measure == "Chi Square":
                # Must have exactly 2 numeric columns
                if num_columns != 2:
                    continue

                # Both columns must be convertible to integers
                try:
                    col1 = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().astype(int)
                    col2 = pd.to_numeric(df.iloc[:, 1], errors='coerce').dropna().astype(int)
                except:
                    continue

                # Check for negative values
                if (col1 < 0).any() or (col2 < 0).any():
                    continue

                # Check equal length after dropping NA
                if len(col1) != len(col2):
                    continue

                # NEW: Check frequency sums are within 1% tolerance
                sum1 = np.sum(col1)
                sum2 = np.sum(col2)

                if sum1 == 0 or sum2 == 0:
                    continue  # Skip if either sum is zero

                percent_diff = abs(sum1 - sum2) / max(sum1, sum2)
                if percent_diff > 0.01:  # 1% tolerance
                    continue

            # GENERAL CHECKS FOR ALL MEASURES
            # Column count rules
            if "exact_columns" in rules and num_columns != rules["exact_columns"]:
                continue
            if "min_columns" in rules and num_columns < rules["min_columns"]:
                continue

            # Check row count using only the required number of numeric columns
            if "min_length" in rules:
                # Allow more columns than exact if needed (especially for correlation-like measures)
                if "exact_columns" in rules:
                    if num_columns < rules["exact_columns"]:
                        continue
                elif "min_columns" in rules:
                    sub_df = numeric_df.iloc[:, :rules["min_columns"]]
                else:
                    sub_df = numeric_df

                valid_rows = sub_df.dropna()
                if valid_rows.shape[0] < rules["min_length"]:
                    continue

            compatible.append(measure)

        return compatible

    @staticmethod
    def get_last_selected_signs():
        instance = Controller.last_stat_instance
        if instance and hasattr(instance, 'n_positive') and hasattr(instance, 'n_negative'):
            print("get last selected signs")
            print(instance.n_positive, instance.n_negative)
            return instance.n_positive, instance.n_negative
        return None, None
