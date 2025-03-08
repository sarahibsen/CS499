import numpy as np
from scipy import stats
import sys 
import pandas as pd
import matplotlib.pyplot as plt
import tkinter 

from scipy.stats import mode
from main_controller import Controller

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
        self.controller = Controller()

        
    def mean(self):
        """
        Return the mean (average) of the data set
        """
        return np.mean(self.data)
    
    def median(self):
        """
        Return the median of the data set
        """
        return np.median(self.data)
    def mode(self):
        """
        Return the mode of the data set
        """
        return mode(self.data)[0][0]
    
    def standardDeviation(self):
        """
        Calculate and return the sample standard deviation of the given data set.
        Returns:
            float: The sample standard deviation of the data.
        """
        # Validate the data
        if not isinstance(self.data, (list, np.ndarray)):
            raise TypeError("Data must be a list or NumPy array of numbers")
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in self.data):
            raise TypeError("All elements in the data must be numbers")
        if len(self.data) == 0:
            raise ValueError("Data cannot be empty")
        
        # Calculate and return the standard deviation
        return np.std(self.data, ddof=1)
    
    def variance(self):
        """
        Calculate and return the sample variance of the given data set.
        Returns:
            float: The sample variance of the data.
        """
        # Validate the data
        if not isinstance(self.data, (list, np.ndarray)):
            raise TypeError("Data must be a list or NumPy array of numbers")
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in self.data):
            raise TypeError("All elements in the data must be numbers")
        if len(self.data) == 0:
            raise ValueError("Data cannot be empty")
        
        # Calculate and return the variance
        return np.var(self.data, ddof=1)

    def coefficientOfVariation(self):
        """
        Calculate and return the coefficient of variation of the given data set.
        Returns:
            float: The coefficient of variation of the data.
        """
        # Validate the data
        if not isinstance(self.data, (list, np.ndarray)):
            raise TypeError("Data must be a list or NumPy array of numbers")
        if not all(isinstance(x, (int, float, np.integer, np.floating)) for x in self.data):
            raise TypeError("All elements in the data must be numbers")
        if len(self.data) == 0:
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

        psequence = list(map(int, input("Enter the percentiles you would like to calculate (e.g. 25, 50, 75): ").split(",")))

        percentiles_array = np.percentile(self.data, psequence, axis=0)

        percentiles_df = pd.DataFrame(
            percentiles_array, 
            columns=[f"Column {i+1}" for i in range(self.data.shape[1])]
        )

        percentiles_df.insert(0, "Percentiles", [f"{p}th" for p in psequence])  # Insert percentile column (Percentiles:, nth, n+1th)
        #is dataframe neeeded for graphing or exporting formatted text? (remove ".to_numpy()")
        return percentiles_df.to_numpy()
    

    
#TODO: Needs frontend aspects for user input
    def probabilityDistribution(self):
        """
        Return the probability distribution of the data set
        """
        #TODO: Tests function's accuracy on output table & graph (needs more example cases)
        loc = float(input("Enter the mean: "))
        scale = float(input("Enter the standard deviation: "))
        size = int(input("Enter the size of the sample: "))
        return np.random.normal(loc, scale, size)
    
    def binomialDistribution(self):
        """
        Return the binomial distribution of the data set
        """
        #TODO: Tests function's accuracy on output table & graph
        n = int(input("Enter the number of trials: "))
        p = float(input("Enter the probability of success: "))
        size = int(input("Enter the size of the sample: "))
        return np.random.binomial(n, p, size)

    @validate_data
    def leastSquareLine(self):
        """
        Only works for interval & frequency datasets
        Parameters: 
            Grabs two arrays (can be np.array) as x and as y columns.
                (e.g. Expected/Actual Freq. Data). 
        Returns:
            the slope, intercept, and equation of the regression line.
        """
        if self.data.shape[1] < 2:
            raise ValueError("Dataset must contain at least two numeric columns.")

        x = self.data.iloc[:, 0]
        y = self.data.iloc[:, 1]

        # Perform linear regression (return values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Equation of the regression line for graphing
        equation = f"y = {slope:.4f}x + {intercept:.4f}"

        return slope, intercept, equation

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
