"""
Loan product and portfolio risk KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

def calc_loan_metrics(df):
    engine = KPIEngine(df)
    kpis = []
    
    if len(df) == 0: 
        return kpis
    
    status_col, status_series = engine.get_column(["loan_status", "status", "payment_status"])
    out_col, out_series = engine.get_numeric(["outstanding_balance", "loan_balance", "remaining_balance"])
    disb_col, disb_series = engine.get_numeric(["disbursed_amount", "loan_amount", "principal"])
    rate_col, rate_series = engine.get_numeric(["interest_rate", "rate", "apr"])

    if out_col is not None:
        total_outstanding = out_series.fillna(0).sum()
        kpis.append(engine.build_kpi(
            category="💰 Loan Analysis", name="Total Outstanding Balance",
            value=f"${total_outstanding:,.2f}", formula="Sum(Outstanding Balance)", source=f"`{out_col}`"
        ))

        if disb_col is not None:
            total_disbursed = disb_series.fillna(0).sum()
            recovery_rate = (total_outstanding / total_disbursed * 100) if total_disbursed > 0 else 0
            kpis.append(engine.build_kpi(
                category="💰 Loan Analysis", name="Loan Recovery Rate",
                value=f"{recovery_rate:.2f}%", formula="Outstanding / Disbursed * 100", source=f"`{out_col}`, `{disb_col}`"
            ))
        else:
            kpis.append(engine.log_missing("💰 Loan Analysis", "Recovery Rate", "Missing numeric 'disbursed' column."))
    else:
        kpis.append(engine.log_missing("💰 Loan Analysis", "Outstanding Balance", "Missing numeric 'outstanding' column."))

    if status_col is not None:
        kpis.append(engine.build_kpi(
            category="💰 Loan Analysis", name="Total Active Loans",
            value=f"{status_series.nunique()}", formula="Count(Distinct Loan Status)", source=f"`{status_col}`"
        ))

        lower_status = status_series.astype(str).str.lower()
        if "default" in lower_status.unique() or "defaulted" in lower_status.unique():
            default_count = lower_status.isin(["default", "defaulted"]).sum()
            default_rate = (default_count / len(df) * 100) if len(df) > 0 else 0
            kpis.append(engine.build_kpi(
                category="💰 Loan Analysis", name="Loan Default Rate",
                value=f"{default_rate:.2f}%", formula="Defaulted / Total * 100", source=f"`{status_col}`"
            ))
    else:
        kpis.append(engine.log_missing("💰 Loan Analysis", "Loan Status", "Missing 'status' column."))

    if rate_col is not None:
        kpis.append(engine.build_kpi(
            category="💰 Loan Analysis", name="Avg Interest Rate",
            value=f"{rate_series.mean():.2f}%", formula="Mean(Interest Rate)", source=f"`{rate_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💰 Loan Analysis", "Interest Rate", "Missing numeric 'rate' column."))

    return kpis
