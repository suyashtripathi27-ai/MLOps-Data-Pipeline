"""
Store performance, revenue by location, and store profitability metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_store_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    store_col, store_series = engine.get_column(["store_id", "store_name", "store", "outlet_id", "location"])
    rev_col, rev_series = engine.get_numeric(["revenue", "sales", "weekly_sales", "total_sales", "store_revenue"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "order_date", "week_date"])
    
    if store_col is not None:
        kpis.append(engine.build_kpi("🏬 Store", "Total Stores", f"{store_series.nunique()}", "Count(Distinct Stores)", f"`{store_col}`"))
        
        if rev_col is not None:
            calc_df = pd.concat([store_series, rev_series], axis=1).dropna()
            if len(calc_df) > 0:
                store_rev = calc_df.groupby(store_col)[rev_col].sum().sort_values(ascending=False)
                tot_rev = store_rev.sum()
                
                kpis.append(engine.build_kpi("🏬 Store", "Total Store Revenue", f"${tot_rev:,.2f}", "Sum(Store Revenue)", f"`{store_col}`, `{rev_col}`"))
                kpis.append(engine.build_kpi("🏬 Store", "Avg Revenue per Store", f"${store_rev.mean():,.2f}", "Mean(Store Revenue)", f"`{store_col}`, `{rev_col}`"))
                kpis.append(engine.build_kpi("🏬 Store", "Top Performing Store", f"{store_rev.idxmax()} (${store_rev.max():,.2f})", "Max Revenue", f"`{store_col}`, `{rev_col}`"))
                kpis.append(engine.build_kpi("🏬 Store", "Lowest Performing Store", f"{store_rev.idxmin()} (${store_rev.min():,.2f})", "Min Revenue", f"`{store_col}`, `{rev_col}`"))
                
                top_10 = (store_rev.head(10).sum() / tot_rev * 100) if tot_rev > 0 else 0
                kpis.append(engine.build_kpi("🏬 Store", "Top 10 Store Contribution", f"{top_10:.2f}%", "Top 10 / Total * 100", f"`{store_col}`, `{rev_col}`", warnings="High concentration" if top_10 > 70 else "None"))
        else:
            kpis.append(engine.log_missing("🏬 Store", "Store Revenue", "Missing numeric 'revenue'."))
            
        if date_col is not None and rev_col is not None:
            trend_df = pd.concat([store_series, rev_series, date_series], axis=1).dropna()
            if len(trend_df) > 0:
                by_mo = trend_df.groupby([store_col, pd.Grouper(key=date_col, freq="ME")])[rev_col].sum()
                rates = []
                for _, s in by_mo.groupby(level=0):
                    vals = s.values
                    if len(vals) >= 2 and vals[0] != 0:
                        rates.append(((vals[-1] - vals[0]) / vals[0]) * 100)
                if rates:
                    kpis.append(engine.build_kpi("📈 Store Growth", "Avg Store Growth Rate", f"{pd.Series(rates).mean():.2f}%", "Mean(Store Growth)", f"`{store_col}`, `{rev_col}`, `{date_col}`"))
    else:
        kpis.append(engine.log_missing("🏬 Store", "Stores", "Missing 'store_id'."))

    if enable_debug: engine.print_execution_log()
    return kpis
