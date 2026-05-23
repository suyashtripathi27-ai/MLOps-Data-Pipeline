import pandas as pd

def evaluate_kpi_confidence(df, columns, custom_industry_checks=None):
    """
    UNIVERSAL CONFIDENCE SCORER.
    Checks for missing data across any dataset, and applies optional industry-specific rules.
    """
    warnings = []
    score_deduction = 0

    if len(df) == 0:
        return "Low", "Empty dataframe."

    # Universal Check: Missing Data
    for col in columns:
        if col and col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 10:
                warnings.append(f"Missing data in `{col}` (>10%)")
                score_deduction += 15

    # Inject specific checks (e.g., negative downtime in manufacturing, negative age in HR)
    if custom_industry_checks:
        industry_warnings = custom_industry_checks(df)
        if industry_warnings:
            score_deduction += min(40, 10 * len(industry_warnings))
            warnings.extend(industry_warnings)

    # Calculate final baseline
    confidence = "High"
    if score_deduction >= 30:
        confidence = "Low"
    elif score_deduction > 0:
        confidence = "Medium"

    return confidence, ", ".join(warnings) if warnings else "None"
