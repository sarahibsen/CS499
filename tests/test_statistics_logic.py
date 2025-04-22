import pandas as pd
import numpy as np
import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from statisticsLogic import statistic


@pytest.fixture
def numeric_df():
    return pd.DataFrame({
        "A": [10, 20, 30, 40],
        "B": [1.5, 2.5, 3.5, 4.5]
    })


def test_mean(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Mean"](s)
    assert round(result["Mean"], 2) == round(np.mean(numeric_df.values), 2)


def test_median(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Median"](s)
    assert round(result["Median"], 2) == round(np.median(numeric_df.values), 2)


def test_mode(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Mode"](s)
    # Mode returns None if no mode exists
    assert result is None or isinstance(result.get("Mode", {}), dict)



def test_std_dev(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Standard Deviation"](s)
    expected = np.std(numeric_df.values, ddof=1)
    assert round(result["Standard Deviation"], 2) == round(expected, 2)


def test_variance_sample(numeric_df):
    s = statistic(numeric_df)
    result = s.calculate("Variance", "Sample")
    expected = np.var(numeric_df.values, ddof=1)
    assert round(result["Sample Variance"], 2) == round(expected, 2)


def test_variance_population(numeric_df):
    s = statistic(numeric_df)
    result = s.calculate("Variance", "Population")
    expected = np.var(numeric_df.values, ddof=0)
    assert round(result["Population Variance"], 2) == round(expected, 2)


def test_coeff_variation(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Coefficient of Variation"](s)
    assert "Coefficient of Variation" in result
    assert isinstance(result["Coefficient of Variation"], float)


def test_percentiles_quartiles(numeric_df):
    s = statistic(numeric_df)
    result = s.calculate("Percentiles", option="Quartiles (25, 50, 75)")
    assert "Percentiles" in result
    assert len(result["Percentiles"]) == 3


def test_probability_distribution_normal(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Probability Distribution"](s, option="Normal")
    assert result["Distribution"] == "Normal"
    assert isinstance(result["Mean"], float)
    assert isinstance(result["Standard Deviation"], float)


def test_probability_distribution_pdf(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Probability Distribution"](s, option="PDF")
    assert result["Distribution"] == "PDF"
    assert "PDF Values" in result


def test_probability_distribution_cdf(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Probability Distribution"](s, option="CDF")
    assert result["Distribution"] == "CDF"
    assert "CDF Values" in result


def test_binomial_distribution(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Binomial Distribution"](s)
    assert "Binomial Distribution" in result
    assert len(result["Binomial Distribution"]) == len(numeric_df)


def test_rank_sum(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Rank Sum"](s)
    assert "U-Statistic" in result
    assert "P-Value" in result


def test_spearman_correlation(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Spearman Correlation"](s)
    assert "Spearman Correlation" in result
    assert "P-Value" in result


def test_sign_test(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Sign Test"](s)
    assert "P-Value" in result


def test_least_square_line(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Least Square Line"](s)
    assert "Slope" in result
    assert "Y-Intercept" in result


def test_correlation_coefficient(numeric_df):
    s = statistic(numeric_df)
    result = statistic.registered_measures["Correlation Coefficient"](s)
    assert "R Value (Correlation Coefficient)" in result


def test_chi_square():
    df = pd.DataFrame({
        "Expected": [10, 20, 30],
        "Observed": [11, 19, 30]  
    })
    s = statistic(df)
    result = statistic.registered_measures["Chi Square"](s, expected="Expected", observed="Observed")
    assert result is not None
    assert "Chi-Squared Statistic" in result

