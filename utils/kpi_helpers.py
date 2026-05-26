import pandas as pd
from utils.confidence_engine import evaluate_kpi_confidence

# ==========================================
# 1. SMART COLUMN ROUTING
# ==========================================

def first_column(df, candidates):
    """
    Finds the first matching column in the dataframe from a list of candidates.
    100% CASE-INSENSITIVE to prevent data-mapping failures.
    """
    if df is None or df.empty:
        return None
        
    lower_candidates = [str(col).lower().strip() for col in candidates]
    
    for actual_col in df.columns:
        if str(actual_col).lower().strip() in lower_candidates:
            return actual_col 
            
    return None


# ==========================================
# 2. SAFETY MIDDLEWARE (Crash Prevention)
# ==========================================

def safe_exists(df, col):
    """Safely checks if a column alias was found AND exists in the DataFrame."""
    return col is not None and col in df.columns

def safe_numeric(df, col):
    """Safely checks if a column exists and is inherently numeric."""
    return safe_exists(df, col) and pd.api.types.is_numeric_dtype(df[col])

def safe_datetime(df, col):
    """Safely checks if a column exists and can be parsed as dates."""
    if not safe_exists(df, col):
        return False
        
    # Fast-path: Already a datetime object
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        return True
        
    # Safe check: Attempt to convert a tiny sample without crashing
    first_valid = df[col].dropna().iloc[0:1]
    if first_valid.empty:
        return False
        
    try:
        pd.to_datetime(first_valid, errors='raise')
        return True
    except (ValueError, TypeError):
        return False


# ==========================================
# 3. KPI FORMATTING & DATA CLEANING
# ==========================================

def safe_kpi(category, name, value, formula, source, confidence, warnings):
    """Standardizes the dictionary output for every KPI across all industries."""
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
