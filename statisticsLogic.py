import tkinter.simpledialog
import numpy as np
from scipy import stats
from statistics import mode
import sys 
import pandas as pd
import matplotlib.pyplot as plt
import tkinter 

from scipy.stats import mode, norm
from tkinter import simpledialog, messagebox


import tkinter
from tkinter import Toplevel, Label, Radiobutton, Button, StringVar, W
import sys # To check for existing root
from data_utils import clean_numeric_data


class statistic():
    """
    Equations for calculating statistics on a dataset 
    Parameters: 
        - The name of the measure 
        - The data type that the measure can calculate on
    """
    registered_measures = {}

    @classmethod
    def register(cls, name):
        """
        decorator to register measures so that they can be easily called upon
        """
        def decorator(func):
            cls.registered_measures[name] = func
            return func
        return decorator

    measure_requirements = {
        "Mean": {
            "types": ["int", "float", "double"],
            "min_columns": 1
        },
        "Median": {
            "types": ["int", "float", "double"],
            "min_columns": 1
        },
        "Mode": {
            "types": ["int", "float", "double"],
            "min_columns": 1
        },
        "Standard Deviation": {
            "types": ["int", "float", "double"],
            "min_columns": 1,
            "min_length": 2
        },
        "Variance": {
            "types": ["int", "float", "double"],
            "min_columns": 1,
            "min_length": 1
        },
        "Coefficient of Variation": {
            "types": ["int", "float", "double"],
            "min_columns": 1,
            "min_length": 1
        },
        "Percentiles": {
            "types": ["int", "float", "double"],
            "min_columns": 1
        },
        "Probability Distribution": {
            "types": ["int", "float", "double"],
            "min_columns": 1,
            "requires_std_dev": True
        },
        "Binomial Distribution": {
            "types": ["int", "float"],
            "min_columns": 1,
            "min_length": 1
        },
        "Least Square Line": {
            "types": ["int", "float", "double"],
            "exact_columns": 2,
            "requires_equal_length": True,
            "min_length": 2
        },
        "Chi Square": {
            "types": ["int"],
            "exact_columns": 2,
            "requires_equal_length": True,
            "no_negatives": True
        },
        "Correlation Coefficient": {
            "types": ["int", "float", "double"],
            "exact_columns": 2,
            "requires_equal_length": True,
            "min_length": 2
        },
        "Sign Test": {
            "types": ["int", "float", "double"],
            "allowed_columns": [1, 2]
        },
        "Rank Sum": {
            "types": ["int", "float", "double"],
            "min_columns": 2,
            "min_length": 1
        },
        "Spearman Rank Correlation": {
            "types": ["int", "float", "double"],
            "exact_columns": 2,
            "requires_equal_length": True,
            "min_length": 3
        }
    }

    measure_options_map = {
        "Variance": ["Population", "Sample"],
        "Percentiles": ["Quartiles (25, 50, 75)", "Median (50)", "Deciles (10, 20, ..., 90)", "90th Percentile", "95th Percentile", "99th Percentile"],
        "Probability Distribution": ["Normal", "PDF", "CDF"],
        "Binomial Distribution": ["Trials and Probability Input"],
        "Sign Test": ["two-sided", "less", "greater"],
    }

    def __init__(self, data):
        self.data = data
#TODO: change this so that we check if the data that was selected by the user
# depending on the data types in the selected data, depends on what statistical functions they can actually use 


    def calculate(self, measure, option=None):
        """
        Perform the calculation for the specified measure.
        """
        cleaned_data = self.data

        if measure == "Mean":
            return {"Mean": np.mean(cleaned_data)}

        elif measure == "Median":
            return {"Median": np.median(cleaned_data)}

        elif measure == "Mode":
            return {"Mode": mode(cleaned_data, keepdims=False).mode[0]}

        elif measure == "Standard Deviation":
            return {"Standard Deviation": np.std(cleaned_data, ddof=1)}

        elif measure == "Variance":
            if option == "Sample":
                return {"Sample Variance": np.var(cleaned_data, ddof=1)}
            return {"Population Variance": np.var(cleaned_data, ddof=0)}

        elif measure == "Coefficient of Variation":
            mean = np.mean(cleaned_data)
            std_dev = np.std(cleaned_data, ddof=1)
            return {"Coefficient of Variation": std_dev / mean}

        elif measure == "Percentiles" and option:
            percentiles = {
                "Quartiles (25, 50, 75)": [25, 50, 75],
                "Median (50)": [50],
                "Deciles (10, 20, ..., 90)": list(range(10, 100, 10)),
                "90th Percentile": [90],
                "95th Percentile": [95],
                "99th Percentile": [99],
            }
            if option in percentiles:
                return {"Percentiles": np.percentile(cleaned_data, percentiles[option], axis=0)}


        raise ValueError(f"Unsupported measure or option: {measure}, {option}")

@statistic.register("Mean")
def mean(self):
    """
    Return the mean (average) of the data set
    """
    cleaned_data = self.data
    return {"Mean": np.mean(cleaned_data)}
    
@statistic.register("Median")
def median(self):
    """
    Return the median of the data set
    """
    cleaned_data = self.data
    return {"Median": np.median(cleaned_data)}
    
@statistic.register("Mode")
def mode(self):
    """
    mode is the only data set in where the user can select multiple data types and still compute 
    """
    cleaned_data = self.data

    if isinstance(self.data, pd.DataFrame):
        result = {}
        for col in self.data.columns:
            counts = self.data[col].value_counts(dropna=True)
            if counts.empty or counts.max() == 1:
                messagebox.showerror("Data Error", "There is no mode in the selected data.")
                raise TypeError("There is no mode in the selected data.")
            else:
                modes = counts[counts == counts.max()].index.tolist()
                result[col] = modes[0] if len(modes) == 1 else modes  # support multimodal

        return {"Mode": result}



    
@statistic.register("Standard Deviation")
def standardDeviation(self):
    """
    Calculate and return the sample standard deviation of the given data set.
    Returns:
        float: The sample standard deviation of the data.

    using an online calculator to confirm results : https://www.calculator.net/standard-deviation-calculator.html?numberinputs=12%2C1%2C1%2C2&ctype=s&x=Calculate
    """
    cleaned_data = self.data
    # Validate the data
    if not isinstance(cleaned_data, (list, np.ndarray)):
        raise TypeError("Data must be a list or NumPy array of numbers")

    # Flatten the data to check for all values // multi column support will still be there
    if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in cleaned_data.flatten()):
        raise TypeError("All elements in the data must be numbers")

    if len(cleaned_data) < 2 :
        return 0 # Prevent errors if all values are zero
        
    # Calculate and return the standard deviation
    return {"Standard Deviation": np.std(cleaned_data, ddof=1)}

@statistic.register("Variance")
def variance(self, variance_type = "Population"):
    """
    Calculate and return the sample variance of the given data set.
    Returns:
        float: The sample variance of the data.
    """

    # TODO: a.any or a.all to check if all values are the same 
    cleaned_data = self.data
    # Validate the data
    if not isinstance(cleaned_data, (list, np.ndarray)):
        raise TypeError("Data must be a list or NumPy array of numbers")
    if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in cleaned_data.flatten()):
        raise TypeError("All elements in the data must be numbers")
    if len(cleaned_data) == 0:
        raise ValueError("Data cannot be empty")
        
    if variance_type == "Sample":
        return {"Sample Variance": np.var(cleaned_data, ddof=1)} # Sample variance
    else:
        return {"Population Variance": np.var(cleaned_data, ddof=0)} # Population variance
        
    # Calculate and return the variance
    return {"Variance": np.var(cleaned_data, ddof=1)}

@statistic.register("Coefficient of Variation")
def coefficientOfVariation(self):
    cleaned_data = self.data
    if not isinstance(cleaned_data, (list, np.ndarray)):
        raise TypeError("Data must be a list or NumPy array of numbers")
    if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in cleaned_data.flatten()):
        raise TypeError("All elements in the data must be numbers")
    if len(cleaned_data) == 0:
        raise ValueError("Data cannot be empty")

    mean = statistic.registered_measures["Mean"](self)["Mean"]
    std_dev = statistic.registered_measures["Standard Deviation"](self)["Standard Deviation"]
    return {"Coefficient of Variation": std_dev / mean}

    
@statistic.register("Percentiles")
def percentiles(self, option=None):
    """
    Calculates percentiles. Accepts either predefined labels or a list of integers from custom input.
    """
    cleaned_data = self.data
    if cleaned_data is None or cleaned_data.size == 0:
        return None

    # Handle default
    selected_percentiles = [25, 50, 75]
    label = "Selected: Quartiles (25, 50, 75)"

    # If user provided a list of raw values (from input box)
    if isinstance(option, list) and all(isinstance(x, int) and 0 <= x <= 100 for x in option):
        selected_percentiles = option
        label = f"Selected: {', '.join(str(p) for p in selected_percentiles)}"

    # Otherwise check if it's a predefined label
    elif isinstance(option, str):
        option_map = {
            "Quartiles (25, 50, 75)": [25, 50, 75],
            "Median (50)": [50],
            "Deciles (10, 20, ..., 90)": list(range(10, 100, 10)),
            "90th Percentile": [90],
            "95th Percentile": [95],
            "99th Percentile": [99],
        }
        if option in option_map:
            selected_percentiles = option_map[option]
            label = f"Selected: {option}"

    self.selected_percentiles = selected_percentiles
    self.selected_percentile_label = label

    percentile_values = np.percentile(cleaned_data, selected_percentiles, axis=0)

    return {
        "Percentiles": percentile_values,
        "Selected": label
    }


        
@statistic.register("Probability Distribution")
def probabilityDistribution(self, option=None):
    cleaned_data = self.data
    if cleaned_data is None or cleaned_data.size == 0:
        messagebox.showerror("Data Error", "Cannot calculate distribution on empty or invalid data.")
        return None

    mean_val = np.mean(cleaned_data)
    std_dev_val = np.std(cleaned_data)
    if std_dev_val <= 0:
        messagebox.showerror("Calculation Error", "Standard deviation is zero or negative.")
        return None

    if not option:
        option = "Normal"

    choice = option.lower().strip()

    # Flatten to 1D for simplicity
    flat_data = cleaned_data.flatten()
    flat_data = np.sort(flat_data)

    if choice == 'normal':
        return {
            "Distribution": "Normal",
            "Mean": mean_val,
            "Standard Deviation": std_dev_val
        }

    elif choice == 'pdf':
        pdf_values = norm.pdf(flat_data, mean_val, std_dev_val)
        return {
            "Distribution": "PDF",
            "Mean": mean_val,
            "Standard Deviation": std_dev_val,
            "PDF Values": pdf_values.tolist(),
            "X": flat_data.tolist()
        }

    elif choice == 'cdf':
        cdf_values = norm.cdf(flat_data, mean_val, std_dev_val)
        return {
            "Distribution": "CDF",
            "Mean": mean_val,
            "Standard Deviation": std_dev_val,
            "CDF Values": cdf_values.tolist(),
            "X": flat_data.tolist()
        }

    else:
        messagebox.showerror("Option Error", f"Invalid option '{option}' for Probability Distribution.")
        return None





@statistic.register("Binomial Distribution")
def binomialDistribution(self, n=None, p=None):
    selected_data = self.data

    # Fallback to default if not supplied
    n = 10 if n is None or n <= 0 else n
    p = 0.5 if p is None else p

    if not (0 <= p <= 1):
        raise ValueError("Probability must be between 0 and 1.")

    if selected_data is None or len(selected_data) == 0:
        raise ValueError("No valid numeric data selected.")

    return {"Binomial Distribution": np.random.binomial(n, p, len(selected_data))}

    # ----------------------------------------------------------------------------------#
# separating these statistical functions because these are the ones that I have to really hone on
# they are all very specific and need to be tuned for the GUI 
@statistic.register("Least Square Line")
def leastSquareLine(self):
    """
    Only works for interval & frequency datasets
    Returns:
        the slope, intercept, and equation of the regression line.
    """
    cleaned_data = self.data

    if cleaned_data.shape[1] != 2:
        raise ValueError("Least Square Line requires exactly two columns.")

    x, y = cleaned_data.iloc[:, 0].to_numpy(), cleaned_data.iloc[:, 1].to_numpy()

    if len(x) != len(y):
        raise ValueError("Columns must have the same number of values.")

    if len(x) < 2:
        raise ValueError("At least two data points are required.")

    slope, intercept = np.polyfit(x, y, 1)
    equation = f"y = {slope:.3f}x + {intercept:.3f}"

    return {
        "Slope": slope,
        "Intercept": intercept,
        "Equation": equation
    }



@statistic.register("Chi Square")
def chiSquared(self, expected=None, observed=None, rel_tolerance=1e-8):
    """
    Perform Chi-Square test with validation for frequency sums

    Parameters:
    - expected: Column name for expected frequencies (optional)
    - observed: Column name for observed frequencies (optional)
    - rel_tolerance: Relative tolerance for frequency sum agreement (default 1e-8)

    Returns:
    - Dictionary with Chi-Square statistic and p-value
    """
    if not isinstance(self.data, pd.DataFrame):
        messagebox.showerror("Error", "Invalid data for Chi-Square.")
        raise ValueError("Invalid data for Chi-Square.")

    cols = self.data.columns.tolist()

    # Column selection
    expected_col = expected if expected in cols else cols[0]
    observed_col = observed if observed in cols else cols[1] if len(cols) > 1 else None

    if observed_col is None:
        messagebox.showerror("Error", "Chi-square test requires exactly two valid columns.")
        raise ValueError("Chi-square test requires exactly two valid columns.")

    # Convert to numeric and clean data
    try:
        f_exp = pd.to_numeric(self.data[expected_col], errors='coerce').dropna().astype(int)
        f_obs = pd.to_numeric(self.data[observed_col], errors='coerce').dropna().astype(int)
    except Exception as e:
        messagebox.showerror("Error", f"Data conversion error: {str(e)}")
        raise ValueError(f"Data conversion error: {str(e)}")

    # Validation checks
    if len(f_exp) != len(f_obs):
        messagebox.showerror("Error", "Chi-square test requires equal-length data in both columns.")
        raise ValueError("Chi-square test requires equal-length data in both columns")

    if len(f_exp) < 2:
        messagebox.showerror("Error", "Chi-square test requires at least 2 data points.")
        raise ValueError("Chi-square test requires at least 2 data points")

    if np.any(f_exp < 0) or np.any(f_obs < 0):
        messagebox.showerror("Error", "Chi-square test cannot contain negative values.")
        raise ValueError("Chi-square test cannot contain negative values")

    # Percent difference check
    sum_exp = np.sum(f_exp)
    sum_obs = np.sum(f_obs)

    if sum_exp == 0 or sum_obs == 0:
        messagebox.showerror("Error", "Frequency sums cannot be zero.")
        raise ValueError("Frequency sums cannot be zero")

    percent_diff = abs(sum_obs - sum_exp) / max(sum_exp, sum_obs)

    if percent_diff > rel_tolerance:
        error_msg = (
            f"Frequency sums differ by {percent_diff:.2%} (allowed: {rel_tolerance:.2%})\n"
            f"Expected sum: {sum_exp}\n"
            f"Observed sum: {sum_obs}\n"
            "Please normalize your data so sums match."
        )
        messagebox.showerror("Error", error_msg)
        raise ValueError("Please normalize your data so sums match.")

    # Perform Chi-Square test
    try:
        chi_sq_stat, p_value = stats.chisquare(f_obs, f_exp)
        return {
            "Chi-Squared Statistic": f"{chi_sq_stat:.4f}",
            "P-value": f"{p_value:.4e}",
            "Expected Sum": sum_exp,
            "Observed Sum": sum_obs
        }
    except Exception as e:
        messagebox.showerror("Error", f"Chi-square calculation error: {e}")
        return None

@statistic.register("Correlation Coefficient")
def correlationCoefficient(self):
    """
    Best for interval & frequency datasets
    Parameters: 
        grabs two columns of equal length
    Returns:
        the correlation coefficient R Value
    """

    cleaned_data = self.data
    print(cleaned_data)

        # Rows will always have the same number due to the main_controller filling NA with 0's
    if np.isnan(cleaned_data).any():
        messagebox.showerror("Error", "Both columns must have the same row length.")
        raise ValueError("Both columns must have the same row length")
        
        # Checks to ensure number of columns are equal
    if cleaned_data.shape[1] % 2 != 0:
        messagebox.showerror("Error", "The number of columns must be even.")
        raise ValueError("The number of columns must be even")

    x, y = np.hsplit(cleaned_data, 2)

    if len(x) < 2 or len(y) < 2:
        messagebox.showerror("Error", "Correlation Coefficient requires at least 2 data points in each column.")
        raise ValueError("Correlation Coefficient requires at least 2 data points in each column.")

    correlation = np.corrcoef(x.T,y.T)
    correlation_coefficient = correlation[0, 1]  # Extract the correlation coefficient from the matrix
    return {"R Value (Correlation Coefficient)": correlation_coefficient}
    
@statistic.register("Sign Test")
def signTest(self, option=None):
    """
    Performs Sign Test for one-sample or paired-sample with optional multiple hypothesis types.
    If multiple hypothesis options are passed, all are calculated and returned.
    """
    cleaned_data = self.data

    # Determine sample type
    if cleaned_data.shape[1] == 1:
        x = cleaned_data.ravel()
        median = np.median(x)
        diffs = [xi - median for xi in x if xi != median]
    elif cleaned_data.shape[1] == 2:
        x, y = np.hsplit(cleaned_data, 2)
        x = x.ravel()
        y = y.ravel()
        diffs = [xi - yi for xi, yi in zip(x, y) if xi != yi]
    else:
        messagebox.showerror("Sign Test Error", "Data must have one or two numeric columns.")
        return None

    n = len(diffs)
    n_positive = sum(d > 0 for d in diffs)
    n_negative = sum(d < 0 for d in diffs)

    self.n_positive = n_positive
    self.n_negative = n_negative

    # Normalize options
    if isinstance(option, str):
        option = [option]
    elif not option:
        option = ["two-sided"]  # Default

    valid_hypotheses = {"two-sided", "less", "greater"}
    option = [opt for opt in option if opt in valid_hypotheses]

    results = {}
    for hypo in option:
        result = stats.binomtest(n_positive, n, p=0.5, alternative=hypo)
        results[hypo] = {
            "Sign Count (Sign Test)": n,
            "Positive Count (Sign Test)": n_positive,
            "Negative Count (Sign Test)": n_negative,
            "P-Value (Sign Test)": result.pvalue,
            "Alternative (Sign Test)": hypo
        }

    return results if len(results) > 1 else list(results.values())[0]


@statistic.register("Rank Sum")
def rankSum(self):
    """
    Performs the Mann-Whitney U Rank Sum test (non-parametric).
    Requires exactly two numeric columns with non-missing values.
    """
    cleaned_data = self.data
    
    if cleaned_data.shape[1] < 2:
        messagebox.showerror("Rank Sum Error", "You need to select at least two numeric columns.")
        return None

    # Use the first two columns
    try:
        col1, col2 = np.hsplit(cleaned_data[:, :2], 2)
        col1 = col1.ravel()
        col2 = col2.ravel()

        # Remove NaNs (must align lengths)
        col1 = col1[~np.isnan(col1)]
        col2 = col2[~np.isnan(col2)]

        if len(col1) < 2 or len(col2) < 2:
            messagebox.showerror("Rank Sum Error", "Each group needs at least 2 valid values.")
            return None

        stat, p_value = stats.mannwhitneyu(col1, col2, alternative='two-sided')

        return {
            "U-Statistic (Rank Sum)": f"{stat:.4f}",
            "P-Value (Rank Sum)": f"{p_value:.4e}"
        }

    except Exception as e:
        messagebox.showerror("Rank Sum Error", f"An error occurred: {e}")
        return None


@statistic.register("Spearman Rank Correlation")
def spearmanRankCorrelation(self):
    cleaned_data = self.data

    if cleaned_data is None or cleaned_data.shape[1] != 2:
        messagebox.showerror("Input Error", "Spearman Rank Correlation requires exactly two numeric columns.")
        return None

    x = cleaned_data.iloc[:, 0].to_numpy()
    y = cleaned_data.iloc[:, 1].to_numpy()

    if len(x) < 3:
        messagebox.showerror("Input Error", "Spearman Rank Correlation requires at least 3 data points.")
        return None

    try:
        rho, p = stats.spearmanr(x, y)
        return {
            "Spearman Correlation": f"{coef:.4f}",
            "P-Value (Spearman Correlation)": f"{p_value:.4e}"
        }
    except Exception as e:
        messagebox.showerror("Computation Error", f"Failed to compute Spearman correlation: {e}")
        return None



class plotCreation():
    def __init__(self, data):
        """
        Initializes the plotCreation class with a dataset
        """
        self.data = data

    def plot_histogram(self, title = "Histogram"):
        """
        Creates a histogram of the data set 
        Parameters: 
            title (str): the title of the histogram 
        """
        plt.figure()
        plt.hist(self.data, color = 'blue', edgecolor = 'black')
        plt.title(title)
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.show()

    def plot_barChart(self, title="Bar Chart"):
        plt.figure()

        width = 0.3
        x = np.arange(len(self.data.index))  # Number of rows in the dataset
        
        x_labels = self.data.iloc[:, 0]  # First column after index (Percentiles: nth, n+1th)
    
        # Plot each column as a separate bar
        for i, col in enumerate(self.data.columns[1:]):  # Skip 'Percentiles' column
            plt.bar(x + i * width, self.data[col], width=width, label=col)

        plt.xticks(x + width / 2, labels=x_labels)  # Use 'Percentiles' as x-tick labels
        plt.title(title)
        plt.xlabel("Percentiles")
        plt.ylabel("Value")
        plt.legend()
        plt.tight_layout()
        plt.show()


    def plot_lineChart(self, title="Line Plot"):
        """
        Plots a line graph for the dataset using the first column as X and the second as Y.
        If a regression line is present, it overlays it on the plot.
        """
        if self.data.shape[1] < 2:
            raise ValueError("Dataset must contain at least two numeric columns for a line plot.")

        x = self.data.iloc[:, 0]  # First column as x
        y = self.data.iloc[:, 1]  # Second column as y

        plt.figure()
        plt.plot(x, y, marker='o', linestyle='-', color='b', label="Data Points")

        # Try fitting a least square line
        try:
            slope, intercept, equation = statistic(self.data).leastSquareLine()
            plt.plot(x, slope * x + intercept, color='r', linestyle='--', label=f"Regression Line\n{equation}")
        except Exception as e:
            print(f"Could not fit regression line: {e}")

        plt.title(title)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.tight_layout()
        plt.show()



# if __name__ == "__main__":

#     print(statistic.measure_name_map)
