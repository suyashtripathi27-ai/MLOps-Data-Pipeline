"""
Calculates branch performance and efficiency KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

def calc_branch_metrics(df):
    engine = KPIEngine(df)
    kpis = []
    
    if len(df) == 0: 
        return kpis
    
    branch_col, branch_series = engine.get_column(["branch_id", "branch_code", "location", "Geography"])
    amt_col, amt_series = engine.get_numeric(["amount", "balance", "transaction_amount"])

    if branch_col is not None and amt_col is not None:
        # Align index to prevent grouping errors
        df_temp = pd.concat([branch_series, amt_series], axis=1).dropna()
        branch_revenue = df_temp.groupby(branch_col)[amt_col].sum().sort_values(ascending=False)
        
        total_branches = len(branch_revenue)
        total_revenue = branch_revenue.sum()

        kpis.append(engine.build_kpi(
            category="🏢 Branch Analysis", name="Total Branches",
            value=f"{total_branches}", formula="Count(Distinct Branches)", source=f"`{branch_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="🏢 Branch Analysis", name="Avg Branch Revenue",
            value=f"${branch_revenue.mean():,.2f}", formula="Mean(Branch Revenue)", source=f"`{branch_col}`, `{amt_col}`"
        ))

        if total_revenue > 0:
            top_10_share = (branch_revenue.head(10).sum() / total_revenue) * 100
            kpis.append(engine.build_kpi(
                category="🏢 Branch Analysis", name="Top 10 Branch Share",
                value=f"{top_10_share:.1f}%", formula="(Sum of Top 10 / Total) * 100", source=f"`{branch_col}`, `{amt_col}`"
            ))
    else:
        kpis.append(engine.log_missing("🏢 Branch Analysis", "Branch Performance", "Requires 'branch' and numeric 'amount' columns."))

    return kpis
