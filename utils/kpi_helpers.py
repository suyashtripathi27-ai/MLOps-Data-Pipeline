import pandas as pd
from utils.confidence_engine import evaluate_kpi_confidence
from utils.cleaner import smart_parse_dates

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
        sample_parsed = smart_parse_dates(sample)
        # Require the sample to mostly parse as real dates before treating
        # this as a date column at all -- smart_parse_dates never raises
        # (it coerces), so this replaces the old errors='raise' check that
        # used to guard against false-positives on genuinely non-date columns.
        if sample_parsed.notna().sum() / len(sample) < 0.9:
            return None
        parsed_full = smart_parse_dates(df[col])
        if parsed_full.notna().sum() == 0:
            return None
        return parsed_full
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
def confidence_for(df, columns):
    """Wrapper alias for evaluate_kpi_confidence to support legacy imports.
    Every call site in industries/pharma/*.py invokes this as
    confidence_for(df, [col1, col2, ...]) - keep this signature in sync
    with evaluate_kpi_confidence(df, columns, ...)."""
    if df is None or df.empty:
        return "Low", "Empty dataframe."
    try:
        return evaluate_kpi_confidence(df, columns)
    except Exception:
        return "High", "None"
