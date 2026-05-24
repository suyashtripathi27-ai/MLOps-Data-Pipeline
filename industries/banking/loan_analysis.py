"""
Loan product and portfolio risk KPIs.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_loan_metrics(df):
    """Calculates loan portfolio and risk KPIs."""
    kpis = []
    loan_status_col = first_column(df, ["loan_status", "status", "payment_status"])
    outstanding_col = first_column(df, ["outstanding_balance", "loan_balance", "remaining_balance"])
    disbursed_col = first_column(df, ["disbursed_amount", "loan_amount", "principal"])
    rate_col = first_column(df, ["interest_rate", "rate", "apr"])

    if not loan_status_col and not outstanding_col:
        return kpis

    conf, warns = confidence_for(df, [loan_status_col, outstanding_col])
    
    if pd.api.types.is_numeric_dtype(df[outstanding_col]):
        total_outstanding = df[outstanding_col].fillna(0).sum()
        total_loans = df[loan_status_col].nunique()

        kpis.append(safe_kpi(
            category="💰 Loan Analysis",
            name="Total Outstanding Balance",
            value=f"${total_outstanding:,.2f}",
            formula="Sum(Outstanding Balance)",
            source=f"`{outstanding_col}`",
            confidence=conf,
            warnings=warns
        ))
        kpis.append(safe_kpi(
            category="💰 Loan Analysis",
            name="Total Active Loans",
            value=f"{total_loans}",
            formula="Count(Distinct Loan Status)",
            source=f"`{loan_status_col}`",
            confidence=conf,
            warnings=warns
        ))

        status_dist = df[loan_status_col].value_counts()
        if "Default" in status_dist.index or "defaulted" in df[loan_status_col].astype(str).str.lower().unique():
            default_col_values = df[loan_status_col].astype(str).str.lower()
            default_count = (default_col_values.isin(["default", "defaulted"])).sum()
            default_rate = (default_count / len(df) * 100) if len(df) > 0 else 0
            kpis.append(safe_kpi(
                category="💰 Loan Analysis",
                name="Loan Default Rate",
                value=f"{default_rate:.2f}%",
                formula="Defaulted Loans / Total Loans * 100",
                source=f"`{loan_status_col}`",
                confidence=conf,
                warnings=warns
            ))

        if disbursed_col and pd.api.types.is_numeric_dtype(df[disbursed_col]):
            total_disbursed = df[disbursed_col].fillna(0).sum()
            recovery_rate = (total_outstanding / total_disbursed * 100) if total_disbursed > 0 else 0
            kpis.append(safe_kpi(
                category="💰 Loan Analysis",
                name="Loan Recovery Rate",
                value=f"{recovery_rate:.2f}%",
                formula="Outstanding / Disbursed * 100",
                source=f"`{outstanding_col}`, `{disbursed_col}`",
                confidence=conf,
                warnings=warns
            ))

    if rate_col and pd.api.types.is_numeric_dtype(df[rate_col]):
        avg_rate = df[rate_col].mean()
        kpis.append(safe_kpi(
            category="💰 Loan Analysis",
            name="Avg Interest Rate",
            value=f"{avg_rate:.2f}%",
            formula="Mean(Interest Rate)",
            source=f"`{rate_col}`",
            confidence=conf,
            warnings=warns
        ))

    return kpis
