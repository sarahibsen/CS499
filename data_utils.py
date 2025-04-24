import pandas as pd

def clean_numeric_data(df):
    df = df.copy()
    # Strip strings and clean whitespaces
    df = df.astype(str).apply(lambda col: col.str.strip() if col.dtype == 'object' else col)
    # Convert to numeric
    df = df.apply(pd.to_numeric, errors='coerce')
    # Drop all-null columns and rows
    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)
    return df.select_dtypes(include='number')
