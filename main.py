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

class ordinalStatistics:
    '''
    ordinal statistics class
    '''
    def __init__(self, data):
        self.data = data
    
    def median(self):
        stat = statistic(self.data)
        return stat.median()

class discreteStatistics:
    def __init__(self, data):
        self.data = data
    
    def mean(self):
        stat = statistic(self.data)
        return stat.mean()
    
    def variance(self):
        stat = statistic(self.data)
        return stat.variance()

    def standard_deviation(self):
        stat = statistic(self.data)
        return stat.standardDeviation()

class continuousStatistics:
    def __init__(self, data):
        self.data = data
    
    def mean(self):
        stat = statistic(self.data)
        return stat.mean()
    
    def variance(self):
        stat = statistic(self.data)
        return stat.variance()
    
    def standard_deviation(self):
        stat = statistic(self.data)
        return stat.standardDeviation()

    def coefficient_of_variation(self):
        stat = statistic(self.data)
        return stat.coefficientOfVariation()
