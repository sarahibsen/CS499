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

def validate_data(func):
    """Decorator to validate the data before executing a method.
    Changed to make it so where if the user does have characters or strings in their chosen data -- we will just take the
    numerical values not the strings ! : ) 
    """
    def wrapper(self, *args, **kwargs):
        if not isinstance(self.data, (list, np.ndarray, pd.DataFrame)):
            raise TypeError("Data must be a list, NumPy array, or Pandas DataFrame of numbers.")

        # Handle different data types
        if isinstance(self.data, (list, np.ndarray)):
            # Filter out non-numeric values
            self.data = [x for x in self.data if isinstance(x, (int, float, np.integer, np.floating))]

            if len(self.data) == 0:
                raise ValueError("Data cannot be empty or contain only non-numeric values.")

        elif isinstance(self.data, pd.DataFrame):
            # Select only numeric columns
            self.data = self.data.select_dtypes(include=[np.number]).to_numpy()
            
            if len(self.data) == 0:
                raise ValueError("Data cannot be empty or contain only non-numeric values.")
                
        return func(self, *args, **kwargs)
    return wrapper



class statistic():
    """
    Equations for calculating statistics on a dataset 
    Parameters: 

    """
    def __init__(self, data):
        """
        Initializes the Statistics class with a dataset
        """
        self.data = data

        # Binomial distribution values
        self.n = None
        self.p = None

    def _clean_data(self):

        if isinstance(self.data, pd.DataFrame):
            cleaned_data = self.data.select_dtypes(include=[np.number]).to_numpy()
        elif isinstance(self.data, (list, np.ndarray)):
            cleaned_data = np.array(self.data)
        else:
            return []

        # For 1D array
        if cleaned_data.ndim == 1:
            cleaned_data = [x for x in cleaned_data if not pd.isnull(x) and x != 0]
        # For 2D array
        elif cleaned_data.ndim == 2:
            # Remove rows where all values are null or 0
            mask = ~(np.isnan(cleaned_data).all(axis=1) | (cleaned_data == 0).all(axis=1))
            cleaned_data = cleaned_data[mask]

        return cleaned_data if len(cleaned_data) > 0 else np.array([[0]])


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
    
    @validate_data
    def percentiles(self):
        """
        Method applies with ordinal, frequency, and interval
        Parameters:
            numpy.ndarray object, 
            list of percentiles, 
            axis = 0 (for reading columns)
        Returns:
            NumPy ndarray for further processing
        """
        cleaned_data = self._clean_data()
        user_input=simpledialog.askstring("Percentiles", "Enter the percentiles you would like to calculate (e.g. 25, 50, 75): ")
        try:
            psequence = list(map(int, user_input.split(",")))
        except ValueError:
            messagebox.showerror(
                "Percentiles Input Error",
                "Please enter only integers separated by commas (e.g. 25, 50, 75)."
            )
            return None

        percentiles_array = np.percentile(cleaned_data, psequence, axis=0)

        percentiles_df = pd.DataFrame(percentiles_array, columns=[f"Column {i+1}" for i in range(cleaned_data.shape[1])])

        percentiles_df.insert(0, "Percentiles", [f"{p}th" for p in psequence])  # Insert percentile column (Percentiles:, nth, n+1th)
        
        return {"Percentiles": percentiles_df.to_numpy()}

    def probabilityDistribution(self):
        """
        Automatically computes Probability Distribution using the loaded data.
        Mean and standard deviation are calculated directly from the selected data.
        Sample size matches the dataset size.

        Decided to stray away from asking for the users input on this one / this should
        take what the user chooses on the data table

        The values will be needed when we implement plotting. The CDF and PDF will be mostly beneficial 
        for the plot function 
        """
        cleaned_data = self._clean_data()

        # Ask for distribution choice
        distribution_choice = simpledialog.askstring("Distribution", "Choose one: Normal, CDF, PDF")

        if not distribution_choice:
            messagebox.showerror("Error", "Distribution choice is required.")
            return None

        distribution_choice = distribution_choice.lower()
        #x = np.linspace(min(cleaned_data), max(cleaned_data), 100)
        # flatten the data -- because there is a 2D array being passed, there is no min or max values 
        flat = cleaned_data.flatten()
        x = np.linspace(np.min(flat), np.max(flat), 100)

        if distribution_choice == 'normal':
            mean = np.mean(cleaned_data)
            std_dev = np.std(cleaned_data)
            normal_values = norm.pdf(x, mean, std_dev)
            return {"Distribution": "Normal", "Mean": mean, "Standard Deviation": std_dev} #"Values": normal_values.tolist()

        elif distribution_choice == 'pdf':
            mean = np.mean(cleaned_data)
            std_dev = np.std(cleaned_data)
            pdf_values = norm.pdf(x, mean, std_dev)
            return {"Distribution": "PDF", "Mean": mean, "Standard Deviation": std_dev} #"Values": normal_values.tolist()

        elif distribution_choice == 'cdf':
            mean = np.mean(cleaned_data)
            std_dev = np.std(cleaned_data)
            cdf_values = norm.cdf(x, mean, std_dev)
            return {"Distribution": "CDF", "Mean": mean, "Standard Deviation": std_dev} #"Values": normal_values.tolist()

        else:
            messagebox.showerror("Error", "Invalid distribution choice. Please select Normal, PDF, or CDF.")
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

    @validate_data
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

    @validate_data
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
    
    @validate_data
    def signTest(self):
        """
        Parameters:
            grabs either one array (for one-sample sign test) or two arrays of same length (for paired sample sign test),
            user specified alternative hypothesis (H1),
            and default auto method (exact-to-approximate results).
        Returns:
            two floats: the sign test statistic & p-value.
        """
        cleaned_data = self._clean_data()

        # ONE-SAMPLE SIGN TEST
        if cleaned_data.shape[1] == 1:
            x = cleaned_data.ravel()
            print(f"X: {x}")  # Debugging point
            median = np.median(x)
            signs = [xi - median for xi in x if xi != median]
            n = len(signs)
            n_positive = sum(1 for s in signs if s > 0)
            n_negative = sum(1 for s in signs if s < 0)

        # PAIRED SAMPLE SIGN TEST
        elif cleaned_data.shape[1] == 2:
            if np.isnan(cleaned_data).any():
                messagebox.showerror("Paired signTest Error", "Both columns must have the same row length.")
                raise ValueError("Both columns must have the same row length")
            x, y = np.hsplit(cleaned_data, 2)
            x = x.ravel()
            y = y.ravel()
            print(f"X: {x}, Y: {y}")  # Debugging point
            diffs = [xi - yi for xi, yi in zip(x, y) if xi != yi]
            n = len(diffs)
            n_positive = sum(1 for d in diffs if d > 0)
            n_negative = sum(1 for d in diffs if d < 0)

        else:
            messagebox.showerror("signTest Error", "Data must have either one or two columns.")
            raise ValueError("Data must have either one or two columns.")
        
        H_prompt = tkinter.simpledialog.askstring("Alternative Hypothesis", "Choose one: two-sided, less, greater")
        if H_prompt not in ["two-sided", "less", "greater"]:
            tkinter.messagebox.showerror("signTest Error", "Invalid alternative hypothesis. Please choose 'two-sided', 'less', or 'greater'.")
            return None

        result = stats.binomtest(n_positive, n, p=0.5, alternative=H_prompt)

        sign = {"Sign Count": n,
            "Positive Count": n_positive,
            "Negative Count": n_negative,
            "P-Value": result.pvalue}

        print(f"Sign Test: {sign}")
        return sign

    @validate_data
    def rankSum(self):
        '''
        Best for ordinal datasets
        Parameters: 
            grabs two arrays (can be different lengths), 
            user specified alternative hypothesis (H1), 
            and default auto method (exact-to-approximate results)
        Returns: 
            two floats: the rank sum statistic & p-value.
        '''
        cleaned_data = self._clean_data()
        
        x, y = np.hsplit(cleaned_data, 2)
        x = x.ravel()
        y = y.ravel()
        # Remove any NaN values from x and y separately
        x = x[~np.isnan(x)]
        y = y[~np.isnan(y)]
        print(f"X: {x}, Y: {y}")  # Debugging point

        H_prompt = tkinter.simpledialog.askstring("Alternative Hypothesis", "Choose one: two-sided, less, greater")

        if H_prompt not in ["two-sided", "less", "greater"]:
            tkinter.messagebox.showerror("rankSum Error", "Invalid alternative hypothesis. Please choose 'two-sided', 'less', or 'greater'.")
            return None

        try:
            result = stats.mannwhitneyu(x, y, method='auto', alternative=H_prompt)
            rank = {"Statistic": result.statistic, "P-Value": result.pvalue}

            print(f"Rank Sum: {rank}")
            return rank
        except Exception as e:
            tkinter.messagebox.showerror("rankSum Error", f"An error occurred while performing the rank sum test: {e}")
            return None

    @validate_data
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

    #TODO: revision, +pie, +curve
    

# # Function to extract numeric columns
# # shouldn't need this function when jarrett implements the loading of csv and the extraction of numerical data from the file 
# # if not, this function will be used to extract the numerical data from the file
# def extract_numeric_data(dataframe):
#     """
#     Extract only numeric columns from a DataFrame and flatten the data.
    
#     Parameters:
#         dataframe (pd.DataFrame): Input DataFrame with mixed data types.
        
#     Returns:
#         np.ndarray: A 1D array of numeric data.
#     """
#     numeric_data = dataframe.select_dtypes(include=[np.number])
#     return numeric_data.to_numpy().flatten()




# if __name__ == "__main__":

#     path = r"C:\Users\matte\Desktop\CS499 - copy\Test Data\IntervalDataTest.csv"
#     try:
#         data = pd.read_csv(path)
#     except Exception as e:
#         print(f"Error reading the file: {e}")
#         exit()


#     print("DataFrame content:\n", data)   
#     numeric_data = data.select_dtypes(include=[np.number])
#     print("Numeric data:\n", numeric_data)

#     # Creating an instance of the Statistic class with the numeric data
#     measure = statistic(numeric_data)

#     standard_deviation = measure.standardDeviation()
#     print("Standard Deviation:", standard_deviation)
#     print("Variance:", measure.variance())
#     print("Coefficient of Variation:", measure.coefficientOfVariation())

#     #leastSquare = measure.leastSquareLine()
#     #print("\n--- Least Square Line ---")
#     #print(leastSquare)

#     #chisquared = measure.chiSquared()
#     #print("\n--- Chi-Squared ---")
#     #print(chisquared)

#     #percentiles_df = measure.percentiles()
#     #print("\n--- Percentiles ---")
#     #print(percentiles_df)

#     #plot vertical bar graph percentiles of 1st column
#     #plotter = plotCreation(percentiles_df)
#     #percentilesbar = plotter.plot_barChart(percentiles_df)
