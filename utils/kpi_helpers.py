import pandas as pd
from utils.confidence_engine import evaluate_kpi_confidence

# ==========================================
# 1. CORE ROUTING
# ==========================================
def first_column(df, candidates):
    if df is None or df.empty: 
        return None
        
    for candidate in candidates:
        lower_cand = str(candidate).lower().strip()
        for actual_col in df.columns:
            if str(actual_col).lower().strip() == lower_cand:
                return actual_col 
    return None

# ==========================================
# 2. COERCION PIPELINES
# ==========================================
def _clean_numeric_strings(series):
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

def safe_numeric_series(df, col):
    """Returns a purely numeric series, or None if impossible."""
    if col not in df.columns: 
        return None
    if pd.api.types.is_numeric_dtype(df[col]): 
        return df[col]
        
    # Coerce and check if it's completely empty (all NaN)
    coerced = pd.to_numeric(_clean_numeric_strings(df[col]), errors="coerce")
    if coerced.isna().all():
        return None
    return coerced

def safe_datetime_series(df, col):
    """Returns a purely datetime series, or None if impossible."""
    if col not in df.columns: 
        return None
    if pd.api.types.is_datetime64_any_dtype(df[col]): 
        return df[col]
    
    sample = df[col].dropna().head(50)
    if sample.empty: 
        return None
        
    try:
        pd.to_datetime(sample, errors='raise')
        return pd.to_datetime(df[col], errors="coerce")
    except (ValueError, TypeError, pd.errors.ParserError):
        return None

# ==========================================
# 3. STANDARDIZED DICTIONARIES
# ==========================================
def safe_kpi(category, name, value, formula, source, confidence, warnings, **kwargs):
    return {
        "category": category, "name": name, "value": value,
        "formula": formula, "source": source, "confidence": confidence,
        "warnings": warnings, **kwargs
    }

def excluded_kpi(category, name, source, reason, **kwargs):
    return safe_kpi(category, name, "EXCLUDED", "N/A", source, "Low", reason, **kwargs)

# ==========================================
# 4. COMPATIBILITY ALIASES
# ==========================================
def confidence_for(metric_name, df=None):
    """Wrapper alias for evaluate_kpi_confidence to support legacy imports."""
    if df is not None and metric_name in df.columns:
        try:
            return evaluate_kpi_confidence(df[metric_name])
        except Exception:
            return "High"
    return "High"
