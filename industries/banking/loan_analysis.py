"""
Loan product and portfolio risk KPIs.
"""
import pandas as pd
from utils.kpi_helpers import (
    first_column, safe_kpi, excluded_kpi, confidence_for, safe_exists, safe_numeric, safe_numeric_series
)

def calc_loan_metrics(df):
    kpis = []
    missing_capabilities = []
    if len(df) == 0: return kpis
    
    loan_status_col = first_column(df, ["loan_status", "status", "payment_status"])
    outstanding_col = first_column(df, ["outstanding_balance", "loan_balance", "remaining_balance"])
    disbursed_col = first_column(df, ["disbursed_amount", "loan_amount", "principal"])
    rate_col = first_column(df, ["interest_rate", "rate", "apr"])

    conf, warns = confidence_for(df, [loan_status_col, outstanding_col, disbursed_col, rate_col])
    
    if safe_numeric(df, outstanding_col):
        clean_outstanding = safe_numeric_series(df, outstanding_col).fillna(0)
        total_outstanding = clean_outstanding.sum()

        kpis.append(safe_kpi(
            category="💰 Loan Analysis", name="Total Outstanding Balance",
            value=f"${total_outstanding:,.2f}", formula="Sum(Outstanding Balance)",
            source=f"`{outstanding_col}`", confidence=conf, warnings=warns
        ))

        if safe_numeric(df, disbursed_col):
            clean_disbursed = safe_numeric_series(df, disbursed_col).fillna(0)
            total_disbursed = clean_disbursed.sum()
            recovery_rate = (total_outstanding / total_disbursed * 100) if total_disbursed > 0 else 0
            
            kpis.append(safe_kpi(
                category="💰 Loan Analysis", name="Loan Recovery Rate",
                value=f"{recovery_rate:.2f}%", formula="Outstanding / Disbursed * 100",
                source=f"`{outstanding_col}`, `{disbursed_col}`", confidence=conf, warnings=warns
            ))
        else:
            missing_capabilities.append("Recovery Rate unavailable: Missing numeric 'disbursed' column.")
    else:
        missing_capabilities.append("Outstanding Balance Analytics unavailable: Missing numeric 'outstanding' column.")

    if safe_exists(df, loan_status_col):
        total_loans = df[loan_status_col].nunique()
        kpis.append(safe_kpi(
            category="💰 Loan Analysis", name="Total Active Loans",
            value=f"{total_loans}", formula="Count(Distinct Loan Status)",
            source=f"`{loan_status_col}`", confidence=conf, warnings=warns
        ))

        status_col_values = df[loan_status_col].astype(str).str.lower()
        if "default" in status_col_values.unique() or "defaulted" in status_col_values.unique():
            default_count = status_col_values.isin(["default", "defaulted"]).sum()
            default_rate = (default_count / len(df) * 100) if len(df) > 0 else 0
            kpis.append(safe_kpi(
                category="💰 Loan Analysis", name="Loan Default Rate",
                value=f"{default_rate:.2f}%", formula="Defaulted / Total * 100",
                source=f"`{loan_status_col}`", confidence=conf, warnings=warns
            ))
    else:
        missing_capabilities.append("Loan Status Analytics unavailable: Missing 'status' column.")

    if safe_numeric(df, rate_col):
        clean_rate = safe_numeric_series(df, rate_col)
        kpis.append(safe_kpi(
            category="💰 Loan Analysis", name="Avg Interest Rate",
            value=f"{clean_rate.mean():.2f}%", formula="Mean(Interest Rate)",
            source=f"`{rate_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("Interest Rate Analytics unavailable: Missing numeric 'rate' column.")

    for missing in missing_capabilities:
        kpis.append(excluded_kpi(category="⚠️ System Audit", name="Data Gap Detected", source="Diagnostic", reason=missing))

    return kpis
