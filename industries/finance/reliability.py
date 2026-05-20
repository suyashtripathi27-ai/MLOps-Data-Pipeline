"""
Corporate Finance Data Governance & Reliability Checks
"""
import pandas as pd

def _first_column(df, candidates):
    """Helper to flexibly find columns even if headers vary slightly across accounting systems."""
    for col in candidates:
        if col in df.columns: return col
    return None

def check_financial_sanity_bounds(df):
    """Check 1: Verifies that net income doesn't mathematically exceed revenue bounds."""
    warnings = []
    rev_col = _first_column(df, ["revenue", "gross_revenue", "sales"])
    net_col = _first_column(df, ["net_income", "net_profit", "bottom_line"])
    
    if rev_col and net_col:
        if pd.api.types.is_numeric_dtype(df[rev_col]) and pd.api.types.is_numeric_dtype(df[net_col]):
            # Net income should practically never exceed gross revenue
            violations = (df[net_col] > df[rev_col]).sum()
            if violations > 0:
                warnings.append(f"🔴 CRITICAL: Math Paradox — {violations} records show Net Income exceeding Gross Revenue.")
    return warnings

def check_negative_expense_anomalies(df):
    """Check 2: Flags negative costs or expenses which distort margin calculations."""
    warnings = []
    opex_col = _first_column(df, ["operating_expense", "opex", "operating_cost"])
    cogs_col = _first_column(df, ["cogs", "cost_of_goods_sold", "direct_costs"])
    
    for col in [opex_col, cogs_col]:
        if col and pd.api.types.is_numeric_dtype(df[col]):
            neg_counts = (df[col] < 0).sum()
            if neg_counts > 0:
                warnings.append(f"⚠️ WARNING: {neg_counts} negative entries found in expense column `{col}` (Expected strictly positive values).")
    return warnings

def check_accounting_completeness(df):
    """Check 3: Reviews row-level data for missing critical ledger fields."""
    warnings = []
    critical_fields = [
        _first_column(df, ["revenue", "sales"]),
        _first_column(df, ["operating_expense", "opex"]),
        _first_column(df, ["net_income", "net_profit"])
    ]
    # Filter out None values
    found_critical = [col for col in critical_fields if col is not None]
    
    missing_data = [col for col in found_critical if df[col].isnull().sum() > 0]
    if missing_data:
        warnings.append(f"🔴 CRITICAL: Missing financial data points within core ledger fields: {', '.join(missing_data)}")
    return warnings

def run_finance_governance_checks(df):
    """Conducts rigorous ledger verification and fiduciary data quality audits."""
    warnings = (
        check_financial_sanity_bounds(df) +
        check_negative_expense_anomalies(df) +
        check_accounting_completeness(df)
    )
    return warnings if warnings else ["✅ All baseline financial governance checks passed"]

def evaluate_kpi_confidence(df, columns):
    """
    Standardized MLOps interface. 
    Dynamically computes High/Medium/Low confidence strings based on ledger anomalies.
    """
    warnings = []
    score_deduction = 0

    if len(df) == 0: 
        return "Low", "Empty ledger dataset."

    # Verify column missingness for the current specific calculation block
    for col in columns:
        if col and col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 10: 
                warnings.append(f"Missing data in financial field `{col}` (>10%)")
                score_deduction += 20

    # Run the strict fiduciary tests
    gov_warnings = run_finance_governance_checks(df)
    # Filter out the success placeholder string before compiling real warnings
    real_gov_warnings = [w for w in gov_warnings if "✅" not in w]
    
    if real_gov_warnings:
        score_deduction += min(50, 15 * len(real_gov_warnings))
        warnings.extend(real_gov_warnings)

    confidence = "High"
    if score_deduction >= 35: confidence = "Low"
    elif score_deduction > 0: confidence = "Medium"

    return confidence, ", ".join(warnings) if warnings else "None"
