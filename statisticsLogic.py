import numpy as np
import sys 
import pandas 
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
    
