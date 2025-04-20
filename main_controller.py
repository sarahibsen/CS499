# Refactored Controller as a lightweight Component
import pandas as pd
from Table import TableController, TableModel
from statisticsLogic import statistic
import datetime
from tkinter import filedialog
import numpy as np
from tkinter import messagebox

# adding warning diflection from pandas 
pd.set_option('future.no_silent_downcasting', True)


class Controller:
    """
    A lightweight component class responsible for handling statistical operations
    without storing data.
    """

    last_stat_instance = None

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

        #print(f"Data loaded into Controller:\n{data}")
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
            "Spearman Correlation": stat_instance.spearmanRankCorrelation,
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

        # Only drop rows that are fully NaN in numeric columns
        numeric_df = data_frame.select_dtypes(include='number')

        # Filter rows where at least one numeric column is not null
        data_frame = data_frame[numeric_df.notna().any(axis=1)]

        print("Cleaned numeric data:", data_frame.head())

        compatible = Controller.get_compatible_measures(data_frame)
        incompatible = [m for m in selected_measures if m not in compatible]
        valid = [m for m in selected_measures if m in compatible]

        stat_instance = statistic(data_frame)
        Controller.last_stat_instance = stat_instance

        results = {}
        for m in valid:
            try:
                func = statistic.registered_measures.get(m)

                # Pull optional sub-option (if available)
                options = extra_params.get(m) if extra_params else None

                if m == "Binomial Distribution":
                    n = extra_params.get("n", 10) if extra_params else 10
                    p = extra_params.get("p", 0.5) if extra_params else 0.5
                    result = func(stat_instance, n=n, p=p)

                elif m == "Percentiles":
                    # Combine multiple selected options into one percentile array
                    all_percentile_values = []
                    if options:
                        for opt in options:
                            partial_result = func(stat_instance, option=opt)
                            if partial_result:
                                all_percentile_values.append(partial_result)
                        result = {"Percentiles": all_percentile_values}
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
                    if options and isinstance(options, list):
                        # Just use the first one (since Variance expects one option)
                        result = func(stat_instance, variance_type=options[0])
                    else:
                        result = func(stat_instance, variance_type=(options[0] if options else "Population"))
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
        if measure in ["Mean", "Median", "Chi Square", "Sign Test", "Rank Sum"]:
            return ["Vertical Bar Chart", "Horizontal Bar Chart"]
        elif measure == "Mode":
            return ["Vertical Bar Chart", "Horizontal Bar Chart", "Pie Chart"]
        elif measure in ["Probability Distribution", "Standard Deviation", "Variance", "Coefficient Of Variation"]:
            return ["Normal Distribution Curve"]
        elif measure == "Percentiles":
            return ["Normal Distribution Curve", "Vertical Bar Chart", "Horizontal Bar Chart"]
        elif measure in ["Correlation", "Spearman Correlation", "Least Square Line"]:
            return ["Scatter Plot"]
        elif measure == "Binomial Distribution":
            return ["Vertical Bar Chart", "Normal Distribution Curve"]
        return [" "]


    @staticmethod
    def get_last_binomial_params():
        instance = Controller.last_stat_instance
        if instance and hasattr(instance, 'n') and hasattr(instance, 'p'):
            return instance.n, instance.p
        return None, None

    @staticmethod
    def get_last_selected_percentiles():
        instance = Controller.last_stat_instance
        if instance and hasattr(instance, 'selected_percentiles'):
            return instance.selected_percentile_label, instance.selected_percentiles
        return None, None

    @staticmethod
    def get_compatible_measures(df):
        type_map = TableModel().detect_data_type(df)
        present_types = set(type_map.values())

        return [
            measure for measure, valid_types in statistic.measure_name_map.items()
            if any(t in valid_types for t in present_types)
        ]