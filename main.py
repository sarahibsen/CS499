from statisticsLogic import statistic
import numpy as np


class nominalStatistics:
    '''
    parameters : 
    data : list of data

    '''
    def __init__(self, data):
        self.data = data
    
    def mode(self):
        stat = statistic(self.data)
        return stat.mode()
    
    def frequency(self):
        stat = statistic(self.data)
        return stat.frequency()
    '''
    Plots associated with this data type
    '''
    def piechart(self):
        stat = statistic(self.data)
        return stat.piechart()
    def bargraph(self):
        stat = statistic(self.data)
        return stat.bargraph()
    

class ordinalStatistics:
    '''
    ordinal statistics class
    '''
    def __init__(self, data):
        self.data = data
    
    def proportion(self):
        stat = statistic(self.data)
        return stat.proportion()
    def frequency(self):
        stat = statistic(self.data)
        return stat.frequency()
    def percentiles(self):
        stat = statistic(self.data)
        return stat.percentiles()
    
    '''
    Plots associated with this data type
    '''
    def piechart(self):
        stat = statistic(self.data)
        return stat.piechart()
    def bargraph(self):
        stat = statistic(self.data)
        return stat.bargraph()


class discreteStatistics:
    def __init__(self, data):
        self.data = data
    
    def mean(self):
        stat = statistic(self.data)
        return stat.mean()
    
    def median(self):
        stat = statistic(self.data)
        return stat.median()
    def mode(self):
        stat = statistic(self.data)
        return stat.mode()
    def frequency(self):
        stat = statistic(self.data)
        return stat.frequency()
    def range(self):
        stat = statistic(self.data)
        return stat.range()
    
    '''
    plots associated with this data type
    '''
    def piechart(self):
        stat = statistic(self.data)
        return stat.piechart()
    def bargraph(self):
        stat = statistic(self.data)
        return stat.bargraph()
    

class continuousStatistics:
    def __init__(self, data):
        self.data = data
    
    def mean(self):
        stat = statistic(self.data)
        return stat.mean()
    
    def median(self):
        stat = statistic(self.data)
        return stat.median()
    
    def mode(self):
        stat = statistic(self.data)
        return stat.mode()
    
    def standard_deviation(self):
        stat = statistic(self.data)
        return stat.standardDeviation()

    def percentiles(self):
        stat = statistic(self.data)
        return stat.percentiles()
    
    def range(self):
        stat = statistic(self.data)
        return stat.range()
    
    # check these two if they are calculated correctly
    def correlation(self, data2):
        stat = statistic(self.data)
        return stat.correlation(data2)
    def spearman_correlation(self, data2):
        stat = statistic(self.data)
        return stat.spearman_correlation(data2)
    
    '''
    Plots associated with this data type
    '''
    def histogram(self):
        stat = statistic(self.data)
        return stat.histogram()
    def boxplot(self):
        stat = statistic(self.data)
        return stat.boxplot()
    