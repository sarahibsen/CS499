import numpy as np
import unittest 
import pandas as pd
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from statisticsLogic import statistic


class TestStatisticsFunctions(unittest.TestCase):

    def setUp(self):
        """ Sample data for testing """
        self.valid_data = np.array([1, 2, 3, 4, 5])
        self.invalid_data = ['a', 'b', 'c']  # Invalid data
        self.empty_data = []
        self.mixed_data = np.array([1, 2, 'a', 3])  # Mixed invalid data
        self.data_for_chi_square = pd.DataFrame({
            'Expected': [50, 60, 70],
            'Observed': [45, 65, 75]
        }) # going to use this for least square line as well 
        self.data = np.array([50,60,70,45,65,75])
    
        self.stat_instance_valid = statistic(self.valid_data)
        self.stat_instance_empty = statistic(self.empty_data)
        self.stat_instance_mixed = statistic(self.mixed_data)
        self.stat_instance_chi_square = statistic(self.data_for_chi_square)


    def _clean_data(self):
         """
         Cleans the data by removing NaN values and zeros for statistical calculations.
         """
         cleaned_data = [value for value in self.data if not pd.isnull(value) and value != 0]
         if not cleaned_data:
             return [0]  # Prevent errors if all values are zero
         return cleaned_data


    # ---------- Mean ----------
    def test_mean(self):
        self.assertAlmostEqual(self.stat_instance_valid.mean(), np.mean(self.valid_data), places=5)

    # ---------- Median ----------
    def test_median(self):
        self.assertEqual(self.stat_instance_valid.median(), np.median(self.valid_data))

    # ---------- Mode ----------
    def test_mode(self):
        self.assertEqual(self.stat_instance_valid.mode(), 1)  # Since the first number is mode

    # ---------- Standard Deviation ----------
    def test_standard_deviation(self):
        self.assertAlmostEqual(
            self.stat_instance_valid.standardDeviation(), 
            np.std(self.valid_data, ddof=1), 
            places=5
        )

    # ---------- Variance ----------
    def test_variance(self):
        self.assertAlmostEqual(
            self.stat_instance_valid.variance(), 
            np.var(self.valid_data, ddof=1), 
            places=5
        )

    # ---------- Range ----------
    def test_range(self):
        self.assertEqual(self.stat_instance_valid.range(), np.ptp(self.valid_data))

    # ---------- Coefficient of Variation ----------
    def test_coefficient_of_variation(self):
        cv = np.std(self.valid_data, ddof=1) / np.mean(self.valid_data)
        self.assertAlmostEqual(self.stat_instance_valid.coefficientOfVariation(), cv, places=5)

    # ---------- Percentiles ----------
    def test_percentiles(self):
        self.stat_instance_valid.data = self.valid_data
        with unittest.mock.patch('builtins.input', return_value='25,50,75'):
            percentiles = self.stat_instance_valid.percentiles()
            expected_percentiles = np.percentile(self.valid_data, [25, 50, 75])
            np.testing.assert_array_almost_equal(percentiles[:, 1:], expected_percentiles.reshape(-1, 1))

    # ---------- Probability Distribution ----------
    def test_probability_distribution(self):
        with unittest.mock.patch('builtins.input', side_effect=['0', '1', '100']):
            prob_dist = self.stat_instance_valid.probabilityDistribution()
            self.assertEqual(len(prob_dist), 100)  # Sample size matches input

    # ---------- Chi-Square Test ----------
    def test_chi_square(self):
        chi2_stat, p_value = self.stat_instance_chi_square.chiSquared()
        expected_chi2_stat, _ = pd.DataFrame(self.data_for_chi_square).values.sum(axis=0)
        self.assertAlmostEqual(chi2_stat, expected_chi2_stat, places=5)

    # ---------- Significance Test ----------
    def test_significance_test(self):
        with unittest.mock.patch('builtins.input', side_effect=['0', '1', '100']):
            t_stat, p_value = self.stat_instance_valid.significanceTest()
            self.assertAlmostEqual(t_stat, 0.0, places=5)  # Sample data mean differences = 0


# --------------------------- more complicated statistics ----------------------------
    def test_leastSquareLine(self):
            """
            the line whose total square error is the smallest possible // 
            https://www.mathsisfun.com/data/least-squares-calculator.html
            """
            mid = len(self.data_for_chi_square) // 2
            x = self.data_for_chi_square[:mid]
            y = self.data_for_chi_square[mid:]
            slope, intercept = statistic.leastSquareLine(self.data)
            self.assertAlmostEqual(slope, 1.5, places = 7)
            self.assertAlmostEqual(intercept, 28.33, places = 7)
          
          

if __name__ == "__main__":
    unittest.main()
