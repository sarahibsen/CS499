import numpy as np


class nominalStatistics:
    '''
    nominal statistics class
    '''
    def __init__(self, data):
        self.data = data
    
    def mode(self):
        return self.perform_statistics(self.data, ['mode'], 'nominal')["Mode"]
    
    def frequency(self):
        return self.perform_statistics(self.data, ['frequency'], 'nominal')["Frequency"]
    '''
    Plots associated with this data type
    '''
    def piechart(self):
        return self.perform_statistics(self.data, ['piechart'], 'nominal')["Pie Chart"]
    def bargraph(self):
        return self.perform_statistics(self.data, ['bargraph'], 'nominal')["Bar Graph"]
    

class ordinalStatistics:
    '''
    ordinal statistics class
    '''
    def __init__(self, data):
        self.data = data
    
    def proportion(self):
        return self.perform_statistics(self.data, ['proportion'], 'ordinal')["Proportion"]
    def frequency(self):
        return self.perform_statistics(self.data, ['frequency'], 'ordinal')["Frequency"]
    def percentiles(self):
        return self.perform_statistics(self.data, ['percentiles'], 'ordinal')["Percentiles"]
    
    '''
    Plots associated with this data type
    '''
    def piechart(self):
        return self.perform_statistics(self.data, ['piechart'], 'ordinal')["Pie Chart"]
    def bargraph(self):
        return self.perform_statistics(self.data, ['bargraph'], 'ordinal')["Bar Graph"]


class discreteStatistics:
    def __init__(self, data):
        self.data = data
    
    def mean(self):
        return self.perform_statistics(self.data, ['mean'], 'discrete')["Mean"]
    
    def median(self):
        return self.perform_statistics(self.data, ['median'], 'discrete')["Median"]
    def mode(self):
        return self.perform_statistics(self.data, ['mode'], 'discrete')["Mode"]
    def frequency(self):
        return self.perform_statistics(self.data, ['frequency'], 'discrete')["Frequency"]
    def range(self):
        return self.perform_statistics(self.data, ['range'], 'discrete')["Range"]
    
    '''
    plots associated with this data type
    '''
    def piechart(self):
        return self.perform_statistics(self.data, ['piechart'], 'discrete')["Pie Chart"]
    def bargraph(self):
        return self.perform_statistics(self.data, ['bargraph'], 'discrete')["Bar Graph"]
    

class continuousStatistics:
    def __init__(self, data):
        self.data = data

    
    def mean(self):
        return self.perform_statistics(self.data, ['mean'], 'continuous')["Mean"]
    
    def median(self):
        return self.perform_statistics(self.data, ['median'], 'continuous')["Median"]
    
    def mode(self):
        return self.perform_statistics(self.data, ['mode'], 'continuous')["Mode"]
    
    def standard_deviation(self):
        return self.perform_statistics(self.data, ['standard deviation'], 'continuous')["Standard Deviation"]

    def percentiles(self):
        return self.perform_statistics(self.data, ['percentiles'], 'continuous')["Percentiles"]
    
    def range(self):
        return self.perform_statistics(self.data, ['range'], 'continuous')["Range"]
    
    # check these two if they are calculated correctly
    def correlation(self, data2):
        return self.perform_statistics(self.data, ['correlation'], 'continuous')["Correlation"]
    def spearman_correlation(self, data2):
        return self.perform_statistics(self.data, ['spearman correlation'], 'continuous')["Spearman Correlation"]
    '''
    Plots associated with this data type
    '''
    def histogram(self):
        return self.perform_statistics(self.data, ['histogram'], 'continuous')["Histogram"]
    def boxplot(self):
        return self.perform_statistics(self.data, ['boxplot'], 'continuous')["Box Plot"]