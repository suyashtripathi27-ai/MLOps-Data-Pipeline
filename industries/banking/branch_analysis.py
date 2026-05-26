"""
Calculates branch performance and efficiency KPIs.
"""
import pandas as pd
from utils.kpi_helpers import (
    first_column, safe_kpi, excluded_kpi, confidence_for, safe_exists, safe_numeric, safe_numeric_series
)

def calc_branch_metrics(df):
    kpis = []
    missing_capabilities = []
    
    if len(df) == 0: return kpis
    
    branch_col = first_column(df, ["branch_id", "branch_code", "location", "Geography"])
    amount_col = first_column(df, ["amount", "balance", "transaction_amount"])

    conf, warns = confidence_for(df, [branch_col, amount_col])
    
    if safe_exists(df, branch_col) and safe_numeric(df, amount_col):
        clean_amount = safe_numeric_series(df, amount_col)
        branch_revenue = clean_amount.groupby(df[branch_col]).sum().sort_values(ascending=False)
        
        total_branches = len(branch_revenue)
        total_revenue = branch_revenue.sum()

        kpis.append(safe_kpi(
            category="🏢 Branch Analysis", name="Total Branches",
            value=f"{total_branches}", formula="Count(Distinct Branches)",
            source=f"`{branch_col}`", confidence=conf, warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🏢 Branch Analysis", name="Avg Branch Revenue",
            value=f"${branch_revenue.mean():,.2f}", formula="Mean(Branch Revenue)",
            source=f"`{branch_col}`, `{amount_col}`", confidence=conf, warnings=warns
        ))

        if total_revenue > 0:
            top_10_share = (branch_revenue.head(10).sum() / total_revenue) * 100
            kpis.append(safe_kpi(
                category="🏢 Branch Analysis", name="Top 10 Branch Share",
                value=f"{top_10_share:.1f}%", formula="(Sum of Top 10 / Total) * 100",
                source=f"`{branch_col}`, `{amount_col}`", confidence=conf, warnings=warns
            ))
    else:
        missing_capabilities.append("Branch performance unavailable: Requires 'branch' and numeric 'amount'.")

    for missing in missing_capabilities:
        kpis.append(excluded_kpi(category="⚠️ System Audit", name="Data Gap Detected", source="Diagnostic", reason=missing))

    return kpis
