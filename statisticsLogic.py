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
        elif userChoice == 'percentiles':
            return self.percentiles()
        elif userChoice == 'probability distribution':
            return self.ProbabilityDistribution()
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
    
    def percentiles(self, percentiles):
        """
        Return the specified percentiles for EACH COLUMN in the dataset (not row).
        Parameters:
            percentiles (list): List of percentiles. (temporarily hardcoded an example w/ values [25, 50, 75] at line 152).
        """
        # TODO: Associate choice with H/V Bar graphs, Normal Distribution Curve, X-Y graph.

        result = {}
        for column in self.data.columns:
            result[column] = np.percentile(self.data[column].dropna(), percentiles, axis=0)
        return result
    
    
    def ProbabilityDistribution(self):
        """
        Return the probability distribution of the data set
        """
        loc = input("Enter the mean: ")
        scale = input("Enter the standard deviation: ")
        size = input("Enter the size of the sample: ")
        return np.random.normal(loc, scale, size)
    
    # TODO: set up more of the statistics functions 



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
    path = r"C:\Users\matte\Desktop\CS499 - copy\Test Data\OrdinalDataTest.csv"

    # Load the CSV file
    try:
        data = pd.read_csv(path)
    except Exception as e:
        print(f"Error reading the file: {e}")
        exit()

    # Print the entire DataFrame
    print("DataFrame content:\n", data)
        
    # Extract numeric data
    numeric_data = data.select_dtypes(include=[np.number])
    
    if numeric_data.empty:
        print("No numeric data found in the file.")
        exit()

    # Creating an instance of the Statistic class with the numeric data
    stats = statistic(numeric_data)

    # Calculate the 25th, 50th (median), and 75th percentiles for each column
    percentiles_to_calculate = [25, 50, 75]
    percentiles_result = stats.percentiles(percentiles_to_calculate)

    # Print the results
    for column, values in percentiles_result.items():
        print(f"Percentiles for column '{column}':")
        for p, v in zip(percentiles_to_calculate, values):
            print(f"  {p}th percentile: {v}")

    # Calculating the mean
    print("Mean:", stats.mean())


