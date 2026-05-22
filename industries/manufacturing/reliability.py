"""
Manufacturing Data Governance & Reliability Checks
"""

import pandas as pd
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def check_batch_completeness(df):
    warnings = []
    batch_col = _first_column(df, ["batch_number", "batch_id", "lot_number", "lot_id"])
    line_col = _first_column(df, ["production_line", "line_id", "machine_id", "work_center"])
    found_cols = [col for col in [batch_col, line_col] if col is not None]

    missing_critical = [col for col in found_cols if df[col].isnull().sum() > 0]
    if missing_critical:
        warnings.append(f"🔴 CRITICAL: Missing data in core manufacturing columns: {', '.join(missing_critical)}")
    return warnings


def check_negative_output(df):
    output_col = _first_column(df, ["production_volume", "actual_output", "units_produced", "good_units", "scrap_units"])
    if output_col and pd.api.types.is_numeric_dtype(df[output_col]):
        invalid_values = (df[output_col] < 0).sum()
        if invalid_values > 0:
            return [f"⚠️ CRITICAL: {invalid_values} negative values detected in '{output_col}'."]
    return []


def check_defect_spikes(df):
    defect_col = _first_column(df, ["defect_rate", "scrap_rate", "reject_rate"])
    if defect_col and pd.api.types.is_numeric_dtype(df[defect_col]):
        high_defects = (df[defect_col] > 10).sum()
        if high_defects > 0:
            return [f"⚠️ WARNING: {high_defects} rows exceed a 10% defect threshold in '{defect_col}'."]
    return []


def check_downtime(df):
    downtime_col = _first_column(df, ["downtime_hours", "unplanned_downtime", "machine_downtime_hours"])
    if downtime_col and pd.api.types.is_numeric_dtype(df[downtime_col]):
        excessive = (df[downtime_col] > 8).sum()
        if excessive > 0:
            return [f"⚠️ WARNING: {excessive} records show more than 8 hours of downtime in '{downtime_col}'."]
    return []


def run_manufacturing_governance_checks(df):
    return check_batch_completeness(df) + check_negative_output(df) + check_defect_spikes(df) + check_downtime(df)


def evaluate_kpi_confidence(df, columns):
    warnings = []
    score_deduction = 0

    if len(df) == 0:
        return "Low", "Empty dataframe."

    for col in columns:
        if col and col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 10:
                warnings.append(f"Missing data in `{col}` (>10%)")
                score_deduction += 15

    gov_warnings = run_manufacturing_governance_checks(df)
    if gov_warnings:
        score_deduction += min(40, 10 * len(gov_warnings))
        warnings.extend(gov_warnings)

    confidence = "High"
    if score_deduction >= 30:
        confidence = "Low"
    elif score_deduction > 0:
        confidence = "Medium"

    return confidence, ", ".join(warnings) if warnings else "None"
