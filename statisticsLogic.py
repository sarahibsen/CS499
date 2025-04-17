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

"""
Make a radio button class for the measures that need user input
"""
import tkinter
from tkinter import Toplevel, Label, Radiobutton, Button, StringVar, W
import sys # To check for existing root


class statistic():
    """
    Equations for calculating statistics on a dataset 
    Parameters: 
        - The name of the measure 
        - The data type that the measure can calculate on
    """
    measure_name_map = {
        "Mean": ["double", "int", "float"],
        "Median": ["double", "int", "float"],
        "Mode": ["any"],
        "Standard Deviation": ["double", "int", "float"],
        "Variance": ["double", "int", "float"],
        "Coefficient of Variation": ["double", "int", "float"],
        "Percentiles": ["double", "int", "float"],
        "Sign Test": ["double ", "int", "float"],
        "Rank Sum" : ["double ", "int", "float"],
        "Spearman Rank Correlation": ["double ", "int", "float"],
        "Variance": ["double ", "int", "float"]
    }



    measure_options_map = {
        "Variance": ["Population", "Sample"],
        "Percentiles": ["Quartiles (25, 50, 75)", "Median (50)", "Deciles (10, 20, ..., 90)", "90th Percentile", "95th Percentile", "99th Percentile"],
        "Probability Distribution": ["Normal", "PDF", "CDF"],
        "Sign Test": ["two-sided", "less", "greater"],
        "Rank Sum": ["two-sided", "less", "greater"]
        #"Variance"
    }

    def __init__(self, data):
        self.data = data
#TODO: change this so that we check if the data that was selected by the user
# depending on the data types in the selected data, depends on what statistical functions they can actually use 

    def _clean_data(self):
        if isinstance(self.data, pd.DataFrame):
            cleaned_data = self.data.select_dtypes(include=[np.number]).to_numpy()
        elif isinstance(self.data, (list, np.ndarray)):
            cleaned_data = np.array(self.data)
        else:
            return []

        if cleaned_data.ndim == 1:
            cleaned_data = [x for x in cleaned_data if not pd.isnull(x) and x != 0]
        elif cleaned_data.ndim == 2:
            mask = ~(np.isnan(cleaned_data).all(axis=1) | (cleaned_data == 0).all(axis=1))
            cleaned_data = cleaned_data[mask]

        return cleaned_data if len(cleaned_data) > 0 else np.array([[0]])

    def calculate(self, measure, option=None):
        """
        Perform the calculation for the specified measure.
        """
        cleaned_data = self._clean_data()

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
            
        elif measure == "Sign Test":
            return self._sign_test(cleaned_data, option)

        elif measure == "Rank Sum":
            return self._rank_sum(cleaned_data, option)

        # add the others

        raise ValueError(f"Unsupported measure or option: {measure}, {option}")

    def mean(self):
        """
        Return the mean (average) of the data set
        """
        cleaned_data = self._clean_data()
        return {"Mean": np.mean(cleaned_data)}
    
    def median(self):
        """
        Return the median of the data set
        """
        cleaned_data = self._clean_data()
        return {"Median": np.median(cleaned_data)}
    
    def mode(self):
        """
        Return the mode of the data set
        """
        cleaned_data = self._clean_data()
        return {"Mode": mode(cleaned_data, keepdims=False).mode[0]}
    
    def standardDeviation(self):
        """
        Calculate and return the sample standard deviation of the given data set.
        Returns:
            float: The sample standard deviation of the data.

        using an online calculator to confirm results : https://www.calculator.net/standard-deviation-calculator.html?numberinputs=12%2C1%2C1%2C2&ctype=s&x=Calculate
        """
        cleaned_data = self._clean_data()
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
    
    def variance(self, variance_type = "Population"):
        """
        Calculate and return the sample variance of the given data set.
        Returns:
            float: The sample variance of the data.
        """

        # TODO: a.any or a.all to check if all values are the same 
        cleaned_data = self._clean_data()
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

    def coefficientOfVariation(self):
        """
        Calculate and return the coefficient of variation of the given data set.
        Returns:
            float: The coefficient of variation of the data.
        """
        cleaned_data = self._clean_data()
        # Validate the data
        if not isinstance(cleaned_data, (list, np.ndarray)):
            raise TypeError("Data must be a list or NumPy array of numbers")
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in cleaned_data.flatten()):
            raise TypeError("All elements in the data must be numbers")
        if len(cleaned_data) == 0:
            raise ValueError("Data cannot be empty")
        
        # Calculate and return the coefficent of variation
        mean = self.mean()
        std_dev = self.standardDeviation()

        return {"Coefficient of Variation": std_dev['Standard Deviation'] / mean['Mean']}
    

    def percentiles(self):
        """
        Calculates specified percentiles using a RadioButton dialog for selection.
        Method applies with ordinal, frequency, and interval data.

        Returns:
            dict: {"Percentiles": numpy.ndarray} containing the calculated percentiles,
                  or None if the operation is cancelled or fails.
        """
        cleaned_data = self._clean_data()
        if cleaned_data is None:
            print("Percentile calculation cancelled due to data cleaning issues.")
            return None # Stop if cleaning failed
        
        # whatever measure_option is selected will



    

    def probabilityDistribution(self):
        """
        Computes properties related to Normal, PDF, or CDF using the loaded data.
        Mean and standard deviation are calculated from the cleaned data.
        Uses RadioButton dialog for distribution type selection.
        """
        cleaned_data = self._clean_data()
        if cleaned_data is None:
            print("Probability distribution calculation cancelled due to data cleaning issues.")
            return None # Stop if cleaning failed
        if cleaned_data.size == 0:
             messagebox.showerror("Data Error", "Cannot calculate distribution on empty data.")
             return None

        # --- Define Options for Radio Buttons ---
        option_labels = ["Normal", "PDF", "CDF"] # Keep labels user-friendly

        # --- Use RadioButton Dialog ---
        try:
            dialog = RadioButton(
                title="Select Distribution Type",
                prompt="Choose the distribution characteristic to calculate:",
                options=option_labels
            )
            selected_label = dialog.show() # Show dialog and wait
        except Exception as e:
             messagebox.showerror("GUI Error", f"Failed to create selection dialog: {e}")
             return None

        if selected_label is None:
            print("Probability distribution calculation cancelled by user.")
            return None # User cancelled or closed the window

        # --- Map Selection to Internal Choice ---
        distribution_choice = selected_label.lower() # Convert "Normal" -> "normal", etc.

        # --- Perform Calculations ---
        try:
            # Calculate mean and std dev ONCE, using the entire cleaned dataset
            # np.mean/std on a 2D array calculates over the whole array by default
            mean_val = np.mean(cleaned_data)
            std_dev_val = np.std(cleaned_data)

            # Check for zero standard deviation, which causes issues with norm functions
            if std_dev_val <= 0:
                messagebox.showerror("Calculation Error", "Standard deviation is zero or negative. Cannot calculate distribution.")
                return None

            if distribution_choice == 'normal':
                # norm.pdf(x, mean_val, std_dev_val) # Example calculation if needed
                return {"Distribution": "Normal", "Mean": mean_val, "Standard Deviation": std_dev_val}

            elif distribution_choice == 'pdf':
                # pdf_values = norm.pdf(x, mean_val, std_dev_val)
                return {"Distribution": "PDF", "Mean": mean_val, "Standard Deviation": std_dev_val} # "Values": pdf_values.tolist()

            elif distribution_choice == 'cdf':
                # cdf_values = norm.cdf(x, mean_val, std_dev_val)
                return {"Distribution": "CDF", "Mean": mean_val, "Standard Deviation": std_dev_val} # "Values": cdf_values.tolist()

            else:
                messagebox.showerror("Internal Error", f"Invalid distribution choice '{selected_label}' processed.")
                return None

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred during distribution calculation: {e}")
            return None


    
    def binomialDistribution(self, selected_data):
        """
        Return the binomial distribution of the selected data set.
        The sample size is automatically calculated based on the number of selected data points.

        The binomial distribution is not taking the values that are selected in the data set but
        the number of cells that are selected in the data set.
        """
        # Ask for number of trials
        self.n = tkinter.simpledialog.askinteger("Binomial Distribution", "Enter the number of trials:")
        if self.n is None or self.n <= 0:
            messagebox.showerror("Error", "Number of trials must be a positive integer.")
            return

        # Ask for probability with improved validation
        while True:
            try:
                self.p = float(tkinter.simpledialog.askstring("Binomial Distribution",
                                                              "Enter the probability of success (between 0 and 1):"))
                if 0 <= self.p <= 1:
                    break
                else:
                    messagebox.showerror("Error", "Probability must be between 0 and 1.")
            except ValueError:
                messagebox.showerror("Error", "Invalid probability. Please enter a valid number.")

        # Dynamically calculate sample size
        sample_size = len(selected_data)
        if sample_size <= 0:
            messagebox.showerror("Error", "No data selected for the sample size.")
            return

        # Perform binomial distribution calculation
        return {"Binomial Distribution": np.random.binomial(self.n, self.p, sample_size)}

    # ----------------------------------------------------------------------------------#
# separating these statistical functions because these are the ones that I have to really hone on
# they are all very specific and need to be tuned for the GUI 
    def leastSquareLine(self):
        """
        Only works for interval & frequency datasets
        Parameters: 
            Grabs two arrays (can be np.array) as x and as y columns.
                (e.g. Expected/Actual Freq. Data). 
        Returns:
            the slope, intercept, and equation of the regression line.
        """
        cleaned_data = self._clean_data()
        # the user should be able to choose their own columns--however, they must be the same length 

        # Rows will always have the same number due to the main_controller filling NA with 0's
        if np.isnan(cleaned_data).any():
            messagebox.showerror("Error", "Both columns must have the same row length.")
            raise ValueError("Both columns must have the same row length")
        
        # Checks to ensure number of columns are equal
        if cleaned_data.shape[1] % 2 != 0:
            messagebox.showerror("Error", "The number of columns must be even.")
            raise ValueError("The number of columns must be even")
        
        x, y = np.hsplit(cleaned_data, 2)
        
        # find the mean of the x and y columns 
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean)** 2)

        if denominator == 0:
            messagebox.showerror("Error", "Denominator is zero. Ensure that you select at least two (x,y) pairs.")
            raise ZeroDivisionError("Cannot divide by zero!")
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        return {"Slope": slope, "Y-Intercept": intercept}


    def chiSquared(self):
        """
        Performs Chi-Square Test using two valid columns of data.
        Returns: the Chi-Square statistic and p-value.
        """
        print(f"Incoming Data to Chi-Squared:\n{self.data}")  # Debugging point
        
        
        if isinstance(self.data, pd.DataFrame):
            if self.data.shape[1] >= 2:
                f_exp = pd.to_numeric(self.data.iloc[:, 0], errors='coerce').dropna().astype(int).values
                f_obs = pd.to_numeric(self.data.iloc[:, 1], errors='coerce').dropna().astype(int).values
            else:
                messagebox.showerror("Error", "Chi-square test requires two valid columns of data.")
                return None

        elif isinstance(self.data, np.ndarray) and self.data.shape[1] >= 2:
            
            f_exp = self.data[:, 0].astype(int)
            f_obs = self.data[:, 1].astype(int)
            
        else:
            messagebox.showerror("Error", "Chi-square test requires two valid columns of data.")
            return None

        print(f"Expected Frequencies: {f_exp}")
        print(f"Observed Frequencies: {f_obs}")

        # Ensure both columns have the same length
        if len(f_exp) != len(f_obs):
            messagebox.showerror("Error", "Chi-square test requires equal-length data in both columns.")
            return None

        # Ensure no negative values (chi-square requires non-negative integers)
        if np.any(f_exp < 0) or np.any(f_obs < 0):
            messagebox.showerror("Error", "Chi-square test cannot contain negative values.")
            return None

        # Perform chi-square test
        try:
            chi_sq_stat, p_value = stats.chisquare(f_obs, f_exp)

            result_str = f"Chi-Square Statistic: {chi_sq_stat:.4f}, P-value: {p_value:.4e}"
            #print(result_str)
            return {"Chi-Squared Statistic": f"{chi_sq_stat}", "P-value": f"{p_value}"}

        except Exception as e:
            messagebox.showerror("Error", f"Chi-square calculation error: {e}")
            return None

    def correlationCoefficient(self):
        """
        Best for interval & frequency datasets
        Parameters: 
            grabs two columns of equal length
        Returns:
            the correlation coefficient R Value
        """

        cleaned_data = self._clean_data()

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
    

    def signTest(self):
        """
        Perform a one-sample or paired-sample Sign Test using a GUI RadioButton to select the alternative hypothesis.
        Returns a dictionary with counts and the p-value.
        """
        cleaned_data = self._clean_data()

        if cleaned_data.shape[1] == 1:
            x = cleaned_data.ravel()
            median = np.median(x)
            diffs = [xi - median for xi in x if xi != median]
            n = len(diffs)
            n_positive = sum(1 for d in diffs if d > 0)
            n_negative = sum(1 for d in diffs if d < 0)

        elif cleaned_data.shape[1] == 2:
            if np.isnan(cleaned_data).any():
                messagebox.showerror("Sign Test Error", "Both columns must have the same row length.")
                raise ValueError("Both columns must have the same row length")
            x, y = np.hsplit(cleaned_data, 2)
            x = x.ravel()
            y = y.ravel()
            diffs = [xi - yi for xi, yi in zip(x, y) if xi != yi]
            n = len(diffs)
            n_positive = sum(1 for d in diffs if d > 0)
            n_negative = sum(1 for d in diffs if d < 0)

        else:
            messagebox.showerror("Sign Test Error", "Select one or two columns only.")
            raise ValueError("Sign test requires one or two columns of numeric data.")

        try:
            dialog = RadioButton(
                title="Alternative Hypothesis",
                prompt="Choose the alternative hypothesis (H1):",
                options=["two-sided", "less", "greater"]
            )
            selected_hypothesis = dialog.show()
        except Exception as e:
            messagebox.showerror("GUI Error", f"Failed to create hypothesis selection dialog: {e}")
            return None

        if selected_hypothesis is None:
            print("Sign Test cancelled by user.")
            return None

        result = stats.binomtest(n_positive, n, p=0.5, alternative=selected_hypothesis)

        return {
            "Sign Count": n,
            "Positive Count": n_positive,
            "Negative Count": n_negative,
            "P-Value": result.pvalue
        }
    
    def rankSum(self):
        '''
        Performs the Mann-Whitney U rank sum test on the first two numeric columns.
        Ensures it works on a copy of the data to avoid side effects.
        '''
        # 1. Get the cleaned data (should be a copy/new array from _clean_data)
        cleaned_data_result = self._clean_data() # Call the cleaning method

        # Check if cleaning failed or returned None
        if cleaned_data_result is None:
            print("Rank Sum test cancelled due to data cleaning issues or lack of suitable data.")
            return None

        # ***** ADDED STEP: Explicitly make a copy *****
        # Even if _clean_data returns a copy, this guarantees that subsequent
        # slicing/splitting within *this* function won't affect the array
        # potentially cached or used elsewhere.
        cleaned_data = cleaned_data_result.copy()
        # ************************************************

        # 2. Split into two arrays (using first two columns of the COPY)
        try:
            # Ensure we have at least 2 columns in the cleaned data
            if cleaned_data.ndim != 2 or cleaned_data.shape[1] < 2:
                messagebox.showerror("Rank Sum Error", "Cleaned data does not have at least two columns for Rank Sum test.")
                return None

            data_to_split = cleaned_data[:, :2] # Slice the first two columns of the copy
            x, y = np.hsplit(data_to_split, 2)
            x = x.ravel()
            y = y.ravel()

            # Debugging point using the *local copy*
            print(f"Cleaned X (size {x.size}): {x[:10]}...")
            print(f"Cleaned Y (size {y.size}): {y[:10]}...")

            if x.size == 0 or y.size == 0:
                messagebox.showerror("Rank Sum Error", "One or both data columns became empty after cleaning/splitting.")
                return None

        except Exception as e:
             messagebox.showerror("Data Error", f"An unexpected error occurred during data preparation for Rank Sum: {e}")
             return None


        # 3. Get Alternative Hypothesis using RadioButton Dialog
        hypothesis_options = ["two-sided", "less", "greater"]
        try:
            dialog = RadioButton(
                title="Alternative Hypothesis",
                prompt="Choose the alternative hypothesis (H1):",
                options=hypothesis_options
            )
            selected_hypothesis = dialog.show()
        except Exception as e:
             messagebox.showerror("GUI Error", f"Failed to create selection dialog: {e}")
             return None

        if selected_hypothesis is None:
            print("Rank Sum test cancelled by user (hypothesis selection).")
            return None


        # 4. Perform Mann-Whitney U Test using the local x, y copies
        try:
            result = stats.mannwhitneyu(x, y, method='auto', alternative=selected_hypothesis)
            rank_results = {"Statistic": result.statistic, "P-Value": result.pvalue}

            print(f"Rank Sum Test Results: {rank_results}")
            # 5. Return the result. The original self.data remains untouched by rankSum's internal steps.
            return rank_results

        except ValueError as ve:
             messagebox.showerror("Rank Sum Error", f"Calculation error during rank sum test: {ve}")
             return None
        except Exception as e:
            messagebox.showerror("Rank Sum Error", f"An unexpected error occurred during the rank sum test: {e}")
            return None


    def spearmanRankCorrelation(self):
        """
        Only works for ordinal datasets
        Parameters:
            grabs two arrays from an np.ndarray object
        Returns:
            the spearman rank correlation & p-value.
        """
        cleaned_data = self._clean_data()

        # Rows will always have the same number due to the main_controller filling NA with 0's
        if np.isnan(cleaned_data).any():
            messagebox.showerror("Error", "Both columns must have the same row length.")
            raise ValueError("Both columns must have the same row length")
        
        # Checks to ensure number of columns are equal
        if cleaned_data.shape[1] != 2:
            messagebox.showerror("Error", "The number of columns must be equal to 2 (x,y).")
            raise ValueError("The number of columns must be equal to 2 (x,y)")

        x, y = np.hsplit(cleaned_data, 2)

        if len(x) < 3 or len(y) < 3:
            messagebox.showerror("Error", "Spearman rank correlation requires at least 3 data points in each column.")
            raise ValueError("Spearman rank correlation requires at least 3 data points in each column.")

        spearman = stats.spearmanr(x,y)
        return {"R Value (Spearman Rank Correlation)": spearman.correlation, "P-value (Spearman Rank Correlation)": spearman.pvalue}
    

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
