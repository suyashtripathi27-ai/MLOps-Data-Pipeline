"""
Retail sales, revenue trends, growth, and demand spikes.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine
from utils.validator import SemanticValidator

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_sales_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    rev_col, rev_series = engine.get_numeric(["revenue", "sales", "weekly_sales", "total_sales", "order_value"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "order_date", "week_date", "timestamp"])
    
    if rev_col is not None:
        rev_clean = rev_series.dropna()
        if len(rev_clean) > 0:
            kpis.append(engine.build_kpi("💰 Sales", "Total Revenue", f"${rev_clean.sum():,.2f}", "Sum(Revenue)", f"`{rev_col}`"))
            kpis.append(engine.build_kpi("💰 Sales", "Avg Transaction Value", f"${rev_clean.mean():,.2f}", "Mean(Revenue)", f"`{rev_col}`"))
            kpis.append(engine.build_kpi("💰 Sales", "Median Transaction Value", f"${rev_clean.median():,.2f}", "Median(Revenue)", f"`{rev_col}`"))
            kpis.append(engine.build_kpi("💰 Sales", "Revenue Std Dev", f"${rev_clean.std():,.2f}", "StdDev(Revenue)", f"`{rev_col}`"))
        else:
            kpis.append(engine.log_missing("💰 Sales", "Sales Metrics", "All revenue data is null."))
    else:
        kpis.append(engine.log_missing("💰 Sales", "Sales Metrics", "Missing numeric 'revenue'."))

    if date_col is not None and rev_col is not None:
        trend_df = pd.concat([date_series, rev_series], axis=1).dropna()
        if len(trend_df) > 1:
            weekly = trend_df.set_index(date_col)[rev_col].resample("W").sum().dropna()
            if not weekly.empty:
                growth = ((weekly.iloc[-1] - weekly.iloc[0]) / weekly.iloc[0] * 100) if weekly.iloc[0] != 0 else 0
                kpis.append(engine.build_kpi("📈 Sales Trends", "Revenue Growth %", f"{growth:.2f}%", "((Last - First) / First) * 100", f"`{rev_col}`, `{date_col}`"))
                kpis.append(engine.build_kpi("📈 Sales Trends", "Peak Sales Period", f"{weekly.idxmax().strftime('%Y-%m-%d')} (${weekly.max():,.2f})", "Max weekly revenue", f"`{rev_col}`, `{date_col}`"))
                kpis.append(engine.build_kpi("📈 Sales Trends", "4-Week Moving Average", f"${weekly.rolling(4, min_periods=1).mean().iloc[-1]:,.2f}", "Rolling Mean", f"`{rev_col}`, `{date_col}`"))
                
                spike_thresh = weekly.mean() + (2 * weekly.std())
                spikes = (weekly > spike_thresh).sum()
                kpis.append(engine.build_kpi("📈 Sales Trends", "Demand Spikes Detected", f"{spikes:,}", "Weeks > Mean + 2*StdDev", f"`{rev_col}`, `{date_col}`"))
    
    if enable_debug: engine.print_execution_log()
    return kpis
