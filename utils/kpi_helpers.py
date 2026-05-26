import pandas as pd
from utils.confidence_engine import evaluate_kpi_confidence

# ==========================================
# 1. SMART COLUMN ROUTING (Priority Ranked)
# ==========================================

def first_column(df, candidates):
    """
    Finds the first matching column in the dataframe.
    PRIORITY ROUTED: Respects the exact order of the 'candidates' array.
    """
    if df is None or df.empty:
        return None
        
    # We loop through OUR candidates first to enforce semantic priority!
    for candidate in candidates:
        lower_cand = str(candidate).lower().strip()
        for actual_col in df.columns:
            if str(actual_col).lower().strip() == lower_cand:
                return actual_col 
                
    return None

# ==========================================
# 2. SAFETY MIDDLEWARE (Compute-Optimized)
# ==========================================

def _clean_numeric_strings(series):
    """INTERNAL: Standardizes string cleaning for enterprise numeric coercion."""
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

# ==========================================
# UPDATED SAFETY MIDDLEWARE
# ==========================================
def safe_numeric(df, col):
    """Checks if a column is numeric, using a highly efficient head(100) sample for coercion."""
    if not safe_exists(df, col):
        return False
        
    if pd.api.types.is_numeric_dtype(df[col]):
        return True
        
    sample = df[col].dropna().head(100)
    if sample.empty:
        return False
        
    try:
        # Utilize the DRY helper
        pd.to_numeric(_clean_numeric_strings(sample), errors="raise")
        return True
    except (ValueError, TypeError):
        return False

def safe_datetime(df, col):
    """Checks if a column contains dates using a robust head(50) sample."""
    if not safe_exists(df, col):
        return False
        
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        return True
        
    # Big Data Fix: Test 50 rows to catch mixed-type columns
    sample = df[col].dropna().head(50)
    if sample.empty:
        return False
        
    try:
        pd.to_datetime(sample, errors='raise')
        return True
    except (ValueError, TypeError, pd.errors.ParserError):
        return False

def bool_mask(series):
    """Safely converts representations into Booleans (NaN safe)."""
    return series.fillna("").astype(str).str.lower().isin(["true", "1", "yes", "y", "t"])


# ==========================================
# 3. TRANSFORMATION PIPELINE (The Coercion Layer)
# ==========================================

def safe_numeric_series(df, col):
    """
    Returns a strictly numeric pandas Series ready for math.
    Strips enterprise characters safely using the internal helper.
    """
    if not safe_exists(df, col):
        return pd.Series(dtype=float)

    if pd.api.types.is_numeric_dtype(df[col]):
        return df[col]

    # Utilize the DRY helper
    return pd.to_numeric(_clean_numeric_strings(df[col]), errors="coerce")


# ==========================================
# 4. KPI STANDARDIZATION & GOVERNANCE
# ==========================================

def safe_kpi(category, name, value, formula, source, confidence, warnings, **kwargs):
    """Standardizes KPI output. Extensible via **kwargs."""
    return {
        "category": category,
        "name": name,
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warnings": warnings,
        **kwargs
    }

def excluded_kpi(category, name, source, reason, **kwargs):
    return safe_kpi(category, name, "EXCLUDED", "N/A", source, "Low", reason, **kwargs)

def confidence_for(df, columns):
    valid_columns = [column for column in columns if column and column in df.columns]
    
    if not valid_columns:
        return "Low", "GOVERNANCE_WARNING: MISSING_REQUIRED_COLUMNS"
        
    return evaluate_kpi_confidence(df, valid_columns)
