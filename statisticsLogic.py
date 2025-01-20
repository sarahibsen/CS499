import numpy as np
import sys 
import pandas as pd
import matplotlib.pyplot as plt
import tkinter 


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

    def userChoices(self):
        """
        takes the users input and returns the corresponding answers
        """
        #TODO : this is just a placement function, idk if it is functional 
        userChoice = input("What statistic would you like to use? (mean, median, mode, variance, standard deviation, or coefficient of variation): ")
        if userChoice == 'mean':
            return self.mean()
        elif userChoice == 'median':
            return self.median()
        elif userChoice == 'mode':
            return self.mode()
        elif userChoice == 'variance':
            return self.variance()
        elif userChoice == 'standard deviation':
            return self.standardDeviation()
        elif userChoice == 'coefficient of variation':
            return self.coefficientOfVariation()
        else:
            return "Invalid input"
        
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
        return np.mode(self.data)
    
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
    

    """
    additional math functions needed to add: 
    Percentiles 
    Probability Distribution
    Least Square Line
    Chi Squared
    Correlation Coefficient 
    Rank Sum Test
    Spearman rank correlation coefficient 


    """

    

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

    def plot_barChart(self, title = "Bar Chart"):
        """
        Creates a bar chart of the data set 
        Parameters: 
            title (str): the title of the bar chart 
        """
        pass

    #TODO: create the rest of the functions for plotting <3 
    

# Function to extract numeric columns
def extract_numeric_data(dataframe):
    """
    Extract only numeric columns from a DataFrame and flatten the data.
    
    Parameters:
        dataframe (pd.DataFrame): Input DataFrame with mixed data types.
        
    Returns:
        np.ndarray: A 1D array of numeric data.
    """
    numeric_data = dataframe.select_dtypes(include=[np.number])
    return numeric_data.to_numpy().flatten()

if __name__ == "__main__":
    # Path to the CSV file
    path = r"C:\Users\sarah\Desktop\programs\CS499\Test Data\FrequencyDataTest.csv"

    # Load the CSV file
    try:
        data = pd.read_csv(path)
    except Exception as e:
        print(f"Error reading the file: {e}")
        exit()

    # Extract numeric data
    numeric_data = extract_numeric_data(data)
    
    if numeric_data.size == 0:
        print("No numeric data found in the file.")
        exit()


    # Creating an instance of the Statistic class with the numeric data
    stats = statistic(numeric_data)

    # Calculating the standard deviation
    standard_deviation = stats.standardDeviation()
    print("Standard Deviation:", standard_deviation)
    print("Variance:", stats.variance())
    print("Coefficient of Variation:", stats.coefficientOfVariation())
