"""
Revenue metrics and sales trend analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
# Moderate thresholds - focus on growth velocity vs strict compliance
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,        # ✅ Moderate - tech platforms have data quality
    "score_deduction_for_warning": 12,  # ✅ Lower penalty - more lenient than banking
    "low_confidence_threshold": 35,     # ✅ Higher threshold = harder to flag "Low"
}

def calc_sales_metrics(df, enable_debug=False):
    """
    Calculate sales KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    # ✅ OPTION 2: Initialize with ecommerce industry config
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    
    # ✅ OPTION 1: Enable tracing for enterprise observability
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    if len(df) == 0:
        return kpis
    
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "order_value", "total_sales", "gmv"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "order_date", "timestamp"])
    
    if revenue_col is None:
        kpis.append(engine.log_missing("🛒 Sales Analysis", "Sales Metrics", "Missing numeric 'revenue'."))
        return kpis
    
    total_revenue = revenue_series.sum()
    avg_order_value = revenue_series.mean()
    median_order_value = revenue_series.median()
    variance = revenue_series.var()
    
    kpis.append(engine.build_kpi("🛒 Sales Analysis", "Total Revenue", f"${total_revenue:,.2f}", "Sum(revenue)", f"`{revenue_col}`"))
    kpis.append(engine.build_kpi("🛒 Sales Analysis", "Avg Order Value", f"${avg_order_value:,.2f}", "Mean(order value)", f"`{revenue_col}`"))
    kpis.append(engine.build_kpi("🛒 Sales Analysis", "Median Order Value", f"${median_order_value:,.2f}", "Median(order value)", f"`{revenue_col}`"))
    kpis.append(engine.build_kpi("🛒 Sales Analysis", "Revenue Variance", f"{variance:,.2f}", "Var(order value)", f"`{revenue_col}`"))
    
    if date_col is not None:
        df_temp = pd.concat([date_series, revenue_series], axis=1).dropna()
        
        if len(df_temp) > 1:
            df_temp["month"] = df_temp[date_col].dt.to_period("ME")
            monthly = df_temp.groupby("month")[revenue_col].sum()
            
            if len(monthly) > 0:
                first_period = monthly.iloc[0]
                last_period = monthly.iloc[-1]
                growth = ((last_period - first_period) / first_period * 100) if first_period != 0 else 0
                peak_period = monthly.idxmax().strftime("%Y-%m-%d") if len(monthly) > 0 else "N/A"
                rolling_avg = monthly.rolling(window=3, min_periods=1).mean().iloc[-1]
                
                kpis.append(engine.build_kpi("🛒 Sales Analysis", "Revenue Growth %", f"{growth:.2f}%", "((Last - First) / First) * 100", f"`{revenue_col}`, `{date_col}`"))
                kpis.append(engine.build_kpi("🛒 Sales Analysis", "Peak Revenue Period", peak_period, "ArgMax(Monthly Revenue)", f"`{revenue_col}`, `{date_col}`"))
                kpis.append(engine.build_kpi("🛒 Sales Analysis", "3-Period Moving Average", f"${rolling_avg:,.2f}", "RollingMean(Monthly Revenue, 3)", f"`{revenue_col}`, `{date_col}`"))
    
    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
