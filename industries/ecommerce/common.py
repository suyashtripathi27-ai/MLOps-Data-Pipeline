import pandas as pd
from utils.confidence_engine import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def first_column(df, candidates):
    """Finds the first matching column in the dataframe from a list of candidates."""
    for col in candidates:
        if col in df.columns:
            return col
    return None

def safe_kpi(category, name, value, formula, source, confidence, warnings):
    """Standardizes the dictionary output for every KPI."""
    return {
        "category": category,
        "name": name,
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warnings": warnings,
    }

def excluded_kpi(category, name, source, reason):
    """Gracefully handles broken or excluded metrics without crashing."""
    return safe_kpi(category, name, "EXCLUDED", "N/A", source, "Low", reason)

def bool_mask(series):
    """Safely converts various string/int boolean representations into actual Booleans."""
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y", "t"])

def confidence_for(df, columns):
    """Wrapper to safely check confidence without failing on missing columns."""
    valid_columns = [column for column in columns if column and column in df.columns]
    if not valid_columns:
        return "Low", "No valid columns available."
    return evaluate_kpi_confidence(df, valid_columns)
