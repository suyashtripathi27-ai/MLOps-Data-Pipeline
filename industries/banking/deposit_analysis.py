"""
Deposit-specific KPIs (savings, checking, term deposits).
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Banking industry configuration
# Stricter than default - regulatory compliance demands accuracy
BANKING_CONFIG = {
    "missing_data_threshold": 5,        # ✅ Stricter than default 10% - banking is risk-sensitive
    "score_deduction_for_warning": 20,  # ✅ Higher penalty for quality issues
    "low_confidence_threshold": 25,     # ✅ Lower threshold = easier to flag as "Low"
}

def calc_deposit_metrics(df, enable_debug=False):
    """
    Calculate deposit KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    # ✅ OPTION 2: Initialize with banking industry config for stricter validation
    engine = KPIEngine(df, industry_config=BANKING_CONFIG)
    
    # ✅ OPTION 1: Enable tracing for enterprise observability
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0: 
        return kpis
    
    prod_col, prod_series = engine.get_column(["product_type", "product_name", "account_type"])
    amt_col, amt_series = engine.get_numeric(["amount", "balance", "deposit_amount"])
    int_col, int_series = engine.get_numeric(["interest_earned", "interest_income", "interest_rate"])

    if prod_col is not None and amt_col is not None:
        df_temp = pd.concat([prod_series, amt_series], axis=1).dropna()
        product_summary = df_temp.groupby(prod_col)[amt_col].sum().sort_values(ascending=False)

        if not product_summary.empty:
            total_deposits = product_summary.sum()
            top_product = product_summary.idxmax()
            top_product_share = (product_summary.max() / total_deposits * 100) if total_deposits > 0 else 0

            kpis.append(engine.build_kpi(
                category="🏦 Deposit Analysis", name="Total Deposit Amount",
                value=f"${total_deposits:,.2f}", formula="Sum(Deposit Amount)", source=f"`{prod_col}`, `{amt_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="🏦 Deposit Analysis", name="Top Deposit Product",
                value=f"{top_product} ({top_product_share:.2f}%)", formula="Product with max deposits", source=f"`{prod_col}`, `{amt_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="🏦 Deposit Analysis", name="Deposit Product Count",
                value=f"{len(product_summary)}", formula="Count(Distinct Products)", source=f"`{prod_col}`"
            ))
    else:
        kpis.append(engine.log_missing("🏦 Deposit Analysis", "Product Valuation", "Requires 'product' and numeric 'amount'."))

    if int_col is not None:
        kpis.append(engine.build_kpi(
            category="🏦 Deposit Analysis", name="Total Interest",
            value=f"${int_series.sum():,.2f}", formula="Sum(Interest)", source=f"`{int_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="🏦 Deposit Analysis", name="Avg Interest Rate",
            value=f"{int_series.mean():.2f}%", formula="Mean(Interest Rate)", source=f"`{int_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🏦 Deposit Analysis", "Interest Metrics", "Missing numeric 'interest' column."))

    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
