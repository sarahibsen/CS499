import pandas as pd
import pytest

from statisticsLogic import statistic

@pytest.fixture
def numeric_df():
    return pd.DataFrame({
        "A": [10, 20, 30, 40],
        "B": [1.5, 2.5, 3.5, 4.5]
    })

@pytest.fixture
def mixed_df():
    return pd.DataFrame({
        "A": [10, 20, 30, 40],
        "B": ["a", "b", "c", "d"]
    })

def test_mean_on_numeric(numeric_df):
    stats = statistic(numeric_df)
    result = stats.calculate("mean")
    assert "mean" in result
    assert isinstance(result["mean"], dict)
    assert round(result["mean"]["A"], 2) == 25.0
    assert round(result["mean"]["B"], 2) == 3.0

def test_incompatible_data_skips_string(mixed_df):
    stats = statistic(mixed_df)
    result = stats.calculate("mean")
    assert "mean" in result
    # Column A should be calculated, column B should not
    assert "A" in result["mean"]
    assert "B" not in result["mean"]

def test_median_on_numeric(numeric_df):
    stats = statistic(numeric_df)
    result = stats.calculate("median")
    assert "median" in result
    assert isinstance(result["median"], dict)
    assert round(result["median"]["A"], 2) == 25.0
    assert round(result["median"]["B"], 2) == 3.0

def test_mode_on_numeric(numeric_df):
    stats = statistic(numeric_df)
    result = stats.calculate("mode")
    assert "mode" in result
    assert isinstance(result["mode"], dict)
    assert "A" in result["mode"]
    assert "B" in result["mode"]
    assert result["mode"]["A"] == 0 # No mode for A
    assert result["mode"]["B"] == 0 # no mode for B

def test_variance_on_numeric(numeric_df):
    stats = statistic(numeric_df)
    result = stats.calculate("variance")
    assert "variance" in result
    assert isinstance(result["variance"], dict)
    assert round(result["variance"]["A"], 2) == 250.0
    assert round(result["variance"]["B"], 2) == 2.5