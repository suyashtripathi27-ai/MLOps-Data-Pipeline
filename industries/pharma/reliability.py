"""
Pharma Data Governance & Reliability Checks
"""
import pandas as pd

def run_pharma_governance_checks(df):
    """Conduct strict pharma-specific data quality governance."""
    warnings = []
    
    # Check 1: Clinical data completeness
    critical_columns = ['patient_id', 'adverse_events', 'dosage', 'trial_phase']
    missing_critical = [col for col in critical_columns if col in df.columns and df[col].isnull().sum() > 0]
    if missing_critical:
        warnings.append(f"🔴 CRITICAL: Missing data in pharma columns: {', '.join(missing_critical)}")
    
    # Check 2: Dosage validity (must be positive numbers)
    if 'dosage' in df.columns and pd.api.types.is_numeric_dtype(df['dosage']):
        invalid_dosages = (df['dosage'] <= 0).sum()
        if invalid_dosages > 0:
            warnings.append(f"⚠️ CRITICAL: {invalid_dosages} invalid dosage values (must be positive)")
    
    # Check 3: Adverse events data integrity
    if 'adverse_events' in df.columns:
        ae_count = df['adverse_events'].notna().sum()
        if ae_count < len(df) * 0.5:
            warnings.append("⚠️ WARNING: >50% of adverse events data is missing. Patient safety tracking may be incomplete.")
    
    # Check 4: GMP compliance batch tracking
    if 'batch_number' in df.columns:
        duplicates = df['batch_number'].duplicated().sum()
        if duplicates > 0:
            warnings.append(f"⚠️ WARNING: {duplicates} duplicate batch numbers detected")
    
    # Check 5: Temperature/Storage condition monitoring
    if 'storage_temperature' in df.columns and pd.api.types.is_numeric_dtype(df['storage_temperature']):
        cold_chain_violations = ((df['storage_temperature'] < 2) | (df['storage_temperature'] > 8)).sum()
        if cold_chain_violations > 0:
            warnings.append(f"🔴 CRITICAL: {cold_chain_violations} cold-chain violations detected (pharma requires 2-8°C)")
    
    return warnings if warnings else ["✅ All governance checks passed"]
