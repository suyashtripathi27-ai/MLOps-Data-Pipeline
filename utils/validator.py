import pandas as pd

def check_negative_values(df, columns):
    """Flags any impossible negative values (like negative distances or times)."""
    warnings = []
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                warnings.append(f"⚠️ {neg_count} negative values found in `{col}`.")
    return warnings

def validate_dates(df, start_col, end_col):
    """Flags chronologically impossible dates (e.g., end time before start time)."""
    warnings = []
    if start_col in df.columns and end_col in df.columns:
        invalid_dates = (df[end_col] < df[start_col]).sum()
        if invalid_dates > 0:
            warnings.append(f"⚠️ {invalid_dates} rows where `{end_col}` occurs before `{start_col}`.")
    return warnings
