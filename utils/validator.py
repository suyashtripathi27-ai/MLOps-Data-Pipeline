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

        # A genuine Unix-epoch anomaly (NaN/missing coerced to timestamp 0)
        # shows up as a CLUSTER of dates right around 1970-01-01 -- not
        # merely "the earliest date is before 2000", which would incorrectly
        # reject perfectly legitimate historical data (e.g. bank account
        # opening dates from the 1990s, decades-old manufacturing records).
        years = series.dt.year
        epoch_band_ratio = ((years >= 1969) & (years <= 1971)).mean()
        if epoch_band_ratio > 0.05:
            return False, f"Detected Unix epoch anomaly ({epoch_band_ratio:.1%} of dates cluster around 1970)."

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

        clean = series.dropna()
        if clean.empty:
            return False, "No non-null values to validate."

        # Non-integer check done without astype(int), which raises on any
        # NaN in the original series -- dropna() above already handles
        # that, but doing the modulus check directly (rather than casting)
        # avoids the same crash risk if this function is ever called with
        # a series containing inf or other non-finite values too.
        if clean.min() < 0 or (clean % 1 != 0).any():
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
