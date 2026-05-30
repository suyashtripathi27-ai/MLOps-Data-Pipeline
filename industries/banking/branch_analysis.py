"""
Calculates branch performance and efficiency KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

BANKING_CONFIG = {
    "missing_data_threshold": 5,        
    "score_deduction_for_warning": 20,  
    "low_confidence_threshold": 25,    
}

def calc_branch_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=BANKING_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: 
        return kpis
    
    branch_col, branch_series = engine.get_column(["branch_id", "branch_code", "location", "Geography"])
    amt_col, amt_series = engine.get_numeric(["amount", "balance", "transaction_amount"])

    if branch_col is not None and amt_col is not None:
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
            top_n_kpi = engine.build_dynamic_top_n_kpi("🏢 Branch Analysis", "Branch", branch_revenue, f"`{branch_col}`, `{amt_col}`")
            if top_n_kpi:
                kpis.append(top_n_kpi)
    else:
        kpis.append(engine.log_missing("🏢 Branch Analysis", "Branch Performance", "Requires 'branch' and numeric 'amount' columns."))

    if enable_debug:
        engine.print_execution_log()
    
    return kpis
