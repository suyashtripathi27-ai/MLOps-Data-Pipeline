"""
Pharma Data Governance & Reliability Checks
"""
import pandas as pd

def _first_column(df, candidates):
    """Helper to flexibly find columns even if headers vary slightly."""
    for col in candidates:
        if col in df.columns: return col
    return None

def check_clinical_completeness(df):
    """Check 1: Clinical data completeness."""
    warnings = []
    # Try to find the actual column names used in the dataset
    patient_col = _first_column(df, ['patient_id', 'subject_id', 'participant'])
    ae_col = _first_column(df, ['adverse_events', 'sae_count'])
    dose_col = _first_column(df, ['dosage', 'dose_planned', 'actual_dose'])
    
    found_cols = [col for col in [patient_col, ae_col, dose_col] if col is not None]
    
    missing_critical = [col for col in found_cols if df[col].isnull().sum() > 0]
    if missing_critical:
        warnings.append(f"🔴 CRITICAL: Missing data in core pharma columns: {', '.join(missing_critical)}")
    return warnings

def check_dosage_validity(df):
    """Check 2: Dosage validity (must be positive numbers)."""
    dose_col = _first_column(df, ['dosage', 'dose_planned', 'actual_dose', 'administered_dose'])
    if dose_col and pd.api.types.is_numeric_dtype(df[dose_col]):
        invalid_dosages = (df[dose_col] <= 0).sum()
        if invalid_dosages > 0:
            return [f"⚠️ CRITICAL: {invalid_dosages} invalid dosage values detected (must be strictly positive)."]
    return []

def check_ae_integrity(df):
    """Check 3: Adverse events data integrity."""
    ae_col = _first_column(df, ['adverse_events', 'ae_count', 'complaints'])
    if ae_col:
        ae_missing = df[ae_col].isna().sum()
        if ae_missing > (len(df) * 0.5):
            return [f"⚠️ WARNING: >50% of '{ae_col}' data is missing. Patient safety tracking compromised."]
    return []

def check_gmp_compliance(df):
    """Check 4: GMP compliance batch tracking."""
    batch_col = _first_column(df, ['batch_number', 'batch_id', 'lot_number', 'lot_id'])
    if batch_col:
        duplicates = df[batch_col].duplicated().sum()
        if duplicates > 0:
            return [f"⚠️ WARNING: {duplicates} duplicate batch numbers detected in '{batch_col}'."]
    return []

def check_cold_chain(df):
    """Check 5: Temperature/Storage condition monitoring."""
    temp_col = _first_column(df, ['storage_temperature', 'temp_celsius', 'storage_temp'])
    if temp_col and pd.api.types.is_numeric_dtype(df[temp_col]):
        cold_chain_violations = ((df[temp_col] < 2) | (df[temp_col] > 8)).sum()
        if cold_chain_violations > 0:
            return [f"🔴 CRITICAL: {cold_chain_violations} cold-chain violations detected (pharma requires 2-8°C)."]
    return []

def check_expiry_violations(df):
    """Check 6: Manufacturing vs Expiry timelines."""
    mfg_col = _first_column(df, ["manufacturing_date", "mfg_date"])
    exp_col = _first_column(df, ["expiry_date", "exp_date"])
    if not mfg_col or not exp_col: return []
    
    mfg = pd.to_datetime(df[mfg_col], errors="coerce")
    exp = pd.to_datetime(df[exp_col], errors="coerce")
    violations = int((mfg > exp).sum())
    if violations > 0:
        return [f"🔴 CRITICAL: {violations} batches detected with manufacturing dates AFTER expiry dates."]
    return []

def run_pharma_governance_checks(df):
    """Conduct strict pharma-specific data quality governance."""
    warnings = (
        check_clinical_completeness(df) +
        check_dosage_validity(df) +
        check_ae_integrity(df) +
        check_gmp_compliance(df) +
        check_cold_chain(df) +
        check_expiry_violations(df)
    )
    return warnings

def evaluate_kpi_confidence(df, columns):
    """
    Standardized connection to your pipeline. 
    Calculates the final Confidence Score (High/Medium/Low) based on the governance checks.
    """
    warnings = []
    score_deduction = 0

    if len(df) == 0: return "Low", "Empty dataframe."

    # General missing data checks for the specific KPI being calculated
    for col in columns:
        if col and col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 10: 
                warnings.append(f"Missing data in `{col}` (>10%)")
                score_deduction += 15

    # Run your massive custom Pharma checks
    gov_warnings = run_pharma_governance_checks(df)
    if gov_warnings:
        score_deduction += min(40, 10 * len(gov_warnings))
        warnings.extend(gov_warnings)

    confidence = "High"
    if score_deduction >= 30: confidence = "Low"
    elif score_deduction > 0: confidence = "Medium"

    return confidence, ", ".join(warnings) if warnings else "None"
