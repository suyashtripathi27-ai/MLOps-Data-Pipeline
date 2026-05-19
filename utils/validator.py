import pandas as pd

# ==========================================
# 1. BULK DIAGNOSTICS (For the Technical Appendix)
# ==========================================
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


# ==========================================
# 2. STRICT KPI GATEKEEPER (For Business Logic)
# ==========================================
class SemanticValidator:
    """Checks for semantic corruption to approve or reject specific KPIs."""

    @staticmethod
    def is_valid_datetime(series):
        """Checks if a column is a valid datetime and not a Unix Epoch anomaly."""
        if not pd.api.types.is_datetime64_any_dtype(series):
            return False, "Not a datetime data type."
        
        # Check for Epoch anomalies (e.g., 1970)
        min_year = series.dt.year.min()
        if min_year < 2000:
            return False, f"Detected Unix epoch anomaly (Year {min_year})."
            
        return True, "Valid"

    @staticmethod
    def is_valid_duration(series):
        """Checks if a time duration or distance is semantically valid (no negatives)."""
        if not pd.api.types.is_numeric_dtype(series):
            return False, "Not numeric."
        
        # If more than 5% of the data is negative, the entire metric is considered corrupt
        neg_ratio = (series < 0).mean()
        if neg_ratio > 0.05:
            return False, f"High semantic corruption: {neg_ratio:.1%} of values are negative."
            
        return True, "Valid"

    @staticmethod
    def is_valid_percentage(series):
        """Checks if a percentage metric is bounded 0-100."""
        if not pd.api.types.is_numeric_dtype(series):
            return False, "Not numeric."
        
        # Reject if mathematically impossible percentages exist
        if series.min() < 0 or series.max() > 100:
            return False, f"Out of bounds percentage: min={series.min():.1f}, max={series.max():.1f}."
            
        return True, "Valid"


    @staticmethod
    def is_valid_dosage(series):
        """Pharma: Validates medical dosage (must be positive numbers)."""
        if not pd.api.types.is_numeric_dtype(series):
            return False, "Not numeric."
        
        # Dosages must always be positive
        if series.min() <= 0:
            return False, f"Invalid dosage detected: minimum value is {series.min():.2f} (must be > 0)."
            
        # Flag extremely high outliers (e.g., > 1000x the median)
        median_dosage = series.median()
        if median_dosage > 0 and series.max() > (median_dosage * 1000):
            return False, f"Extreme dosage outlier detected: {series.max():.2f} (>{1000}x median)."
            
        return True, "Valid"

    @staticmethod
    def is_valid_adverse_event_count(series):
        """Pharma: Validates adverse event tracking (must be non-negative integers)."""
        if not pd.api.types.is_numeric_dtype(series):
            return False, "Not numeric."
        
        # Event counts must be non-negative integers
        if series.min() < 0 or (series != series.astype(int)).any():
            return False, "Adverse event counts must be non-negative integers."
            
        return True, "Valid"

    @staticmethod
    def is_valid_gmp_compliance(series):
        """Pharma: Validates GMP inspection results (0 = compliant, >0 = defects)."""
        if not pd.api.types.is_numeric_dtype(series):
            return False, "Not numeric."
        
        # GMP defect counts must be non-negative
        if series.min() < 0:
            return False, "GMP defect counts cannot be negative."
            
        return True, "Valid"
