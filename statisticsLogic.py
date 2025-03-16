import tkinter.simpledialog
import numpy as np
from scipy import stats
import sys 
import pandas as pd
import matplotlib.pyplot as plt
import tkinter 

from scipy.stats import mode
from tkinter import simpledialog, messagebox


def validate_data(func):
    """Decorator to validate the data before executing a method."""
    def wrapper(self, *args, **kwargs):
        if not isinstance(self.data, (list, np.ndarray, pd.DataFrame)):
            raise TypeError("Data must be a list, NumPy array, or Pandas DataFrame of numbers.")
        if isinstance(self.data, (list, np.ndarray)):
            if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in self.data):
                raise TypeError("All elements in the data must be numbers.")
            if len(self.data) == 0:
                raise ValueError("Data cannot be empty.")
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

    def _clean_data(self):
         """
         Cleans the data by removing NaN values and zeros for statistical calculations.
         """
         cleaned_data = [value for value in self.data if not pd.isnull(value) and value != 0]
         if not cleaned_data:
             return [0]  # Prevent errors if all values are zero
         return cleaned_data
       

        
    def mean(self):
        """
        Return the mean (average) of the data set
        """
        cleaned_data = self._clean_data()
        return np.mean(cleaned_data)
    
    def median(self):
        """
        Return the median of the data set
        """
        cleaned_data = self._clean_data()
        return np.median(cleaned_data)
    def mode(self):
        """
        Return the mode of the data set
        """
        cleaned_data = self._clean_data()
        mode_result = stats.mode(cleaned_data, keepdims=True)
        return mode_result.mode[0] if mode_result.mode.size > 0 else None
    
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
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in self.data):
            raise TypeError("All elements in the data must be numbers")
        if len(cleaned_data) < 2 :
            return 0 # Prevent errors if all values are zero
        
        # Calculate and return the standard deviation
        return np.std(cleaned_data, ddof=1)
    
    def variance(self, variance_type = "Population"):
        """
        Calculate and return the sample variance of the given data set.
        Returns:
            float: The sample variance of the data.
        """
        cleaned_data = self._clean_data()
        # Validate the data
        if not isinstance(cleaned_data, (list, np.ndarray)):
            raise TypeError("Data must be a list or NumPy array of numbers")
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in self.data):
            raise TypeError("All elements in the data must be numbers")
        if len(cleaned_data) == 0:
            raise ValueError("Data cannot be empty")
        
        if variance_type == "Sample":
            return np.var(cleaned_data, ddof=1) # Sample variance
        else:
            return np.var(cleaned_data, ddof=0) # Population variance
        
        # Calculate and return the variance
        return np.var(cleaned_data, ddof=1)

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
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in self.data):
            raise TypeError("All elements in the data must be numbers")
        if len(cleaned_data) == 0:
            raise ValueError("Data cannot be empty")
        
        # Calculate and return the coefficient of variation
        mean = self.mean()
        std_dev = self.standardDeviation()
        return std_dev / mean
    
    @validate_data
    def percentiles(self):
        """
        Method applies w/ ordinal, frequency, and interval
        Parameters:
            numpy.ndarray object, list of percentiles, axis 
                (axis=0 for columns, =1 for rows, unspecified for entire dataset)
        Returns:
            NumPy ndarray for further processing
        """
        cleaned_data = self._clean_data()
        psequence = list(map(int, input("Enter the percentiles you would like to calculate (e.g. 25, 50, 75): ").split(",")))

        percentiles_array = np.percentile(cleaned_data, psequence, axis=0)

        percentiles_df = pd.DataFrame(
            percentiles_array, 
            columns=[f"Column {i+1}" for i in range(cleaned_data.shape[1])]
        )

        percentiles_df.insert(0, "Percentiles", [f"{p}th" for p in psequence])  # Insert percentile column (Percentiles:, nth, n+1th)
        #is dataframe neeeded for graphing or exporting formatted text? (remove ".to_numpy()")
        return percentiles_df.to_numpy()
    

    
    def probabilityDistribution(self):
        """
        Automatically computes Probability Distribution using the loaded data.
        Mean and standard deviation are calculated directly from the selected data.
        Sample size matches the dataset size.

        Decided to stray away from asking for the users input on this one / this should
        take what the user chooses on the data table
        """
        cleaned_data = self._clean_data()

        # Compute parameters automatically
        loc = np.mean(cleaned_data)      # Mean
        scale = np.std(cleaned_data)     # Standard Deviation
        size = len(cleaned_data)         # Sample Size (size of dataset)

        if size <= 0:
            raise ValueError("Sample size must be greater than zero.")

        return np.random.normal(loc, scale, size)

    
    def binomialDistribution(self, selected_data):
        """
        Return the binomial distribution of the selected data set.
        The sample size is automatically calculated based on the number of selected data points.

        The binomial distribution is not taking the values that are selected in the data set but 
        the number of cells that are selected in the data set.
        """
        # Ask for number of trials
        n = tkinter.simpledialog.askinteger("Binomial Distribution", "Enter the number of trials:")
        if n is None or n <= 0:
            messagebox.showerror("Error", "Number of trials must be a positive integer.")
            return

        # Ask for probability with improved validation
        while True:
            try:
                p = float(tkinter.simpledialog.askstring("Binomial Distribution", "Enter the probability of success (between 0 and 1):"))
                if 0 <= p <= 1:
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
        return np.random.binomial(n, p, sample_size)

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
        # the user will only be able to grab 2 array's / columns 
        print(f"data : {cleaned_data}")
        mid = len(cleaned_data) // 2 
        x = cleaned_data[:mid]# this should be the first column grabbed 
        # somehow divide the array by two, one half will be assigned to x, the other half will be assigned to y
        # if it is uneven // user did not choose the same length columns 
        y = cleaned_data[mid:]# this will be the second column grabbed 
      #  print(f" x values: {x}")
      #  print(y)
        # add a check to make sure that mid will be divided properly <3 
        if len(x) != len(y):
            messagebox.showerror("Error", "Both columns must have the same length.")
            raise ValueError("Both columns must have the same length")
        
        
        # find the mean of the x and y columns 
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean)** 2)

        if denominator == 0:
            raise ZeroDivisionError("Cannot divide by zero!")
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        return slope, intercept

    @validate_data
    def chiSquared(self):
        """
        Only works for frequency datasets
        Parameters: 
            Grabs two arrays/list from np.ndarray as x,y (expected, actual)
            sum_check=False bypasses invalid/impossible applications of chi-squared
        Returns:
            chi-squared value.
        """
        f_exp = self.data.iloc[:, 0]
        f_obs = self.data.iloc[:, 1]
        chi_sq_results = stats.chisquare(f_obs, f_exp, axis=0, sum_check=False)
        return chi_sq_results

    @validate_data
    def correlationCoefficient(self):
        """
        Only works for interval & frequency datasets
        Parameters: Grabs first column as x and second column as y
        Returns the correlation coefficient.
        """
        return np.corrcoef(self.data.iloc[:, 0], self.data.iloc[:, 1])

    @validate_data
    def significanceTest(self):
        # has known issues w/ parameters that have deprecated since version 1.17.10 of scipy (permutations, alternative hypothesis)
        """
        Only works for interval & frequency datasets
        Parameters: Grabs first column as x and second column as y
        Returns the p-value.
        """
        return stats.ttest_ind(self.data.iloc[:, 0], self.data.iloc[:, 1])

    @validate_data
    def rankSum(self):
        # known issues (alternative hypothesis)
        """
        Only works for ordinal datasets
        Parameters:
            Grabs two arrays (x,y), alternative hypothesis, axis
        Returns:
            the rank sum & p-value as floats
        """
        return stats.ranksums(self.data.iloc[:, 0], self.data.iloc[:, 1])

    @validate_data
    def spearmanRankCorrelation(self):
        """
        Only works for ordinal datasets
        Parameters:
            Grabs two arrays from an np.ndarray object ("x" & "y" column), axis if none ravel/flatten both arrays before performing
                #source https://www.youtube.com/watch?v=XV_W1w4Nwoc
        Returns:
            two floats (the spearman rank correlation & p-value).
        """
        return stats.spearmanr(self.data.iloc[:, 0], self.data.iloc[:, 1], axis = 0)
    

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
