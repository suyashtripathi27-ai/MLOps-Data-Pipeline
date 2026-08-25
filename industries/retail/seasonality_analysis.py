"""
Seasonal patterns, holiday uplift, and demand variability metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_seasonality_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    rev_col, rev_series = engine.get_numeric(["revenue", "sales", "weekly_sales", "total_sales", "order_value"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "order_date", "week_date"])
    hol_col, hol_series = engine.get_column(["is_holiday", "holiday_flag", "holiday"])
    
    if rev_col is not None and date_col is not None:
        work_df = pd.concat([date_series, rev_series], axis=1).dropna()
        if len(work_df) > 0:
            work_df["month"] = work_df[date_col].dt.month
            work_df["quarter"] = work_df[date_col].dt.quarter
            
            monthly = work_df.groupby("month")[rev_col].sum()
            if not monthly.empty:
                kpis.append(engine.build_kpi("📅 Seasonality", "Peak Sales Month", f"Month {int(monthly.idxmax())} (${monthly.max():,.2f})", "Month with max revenue", f"`{rev_col}`, `{date_col}`"))
            
            tot_rev = work_df[rev_col].sum()
            q4_mask = work_df["quarter"] == 4
            q4_rev = work_df.loc[q4_mask, rev_col].sum()
            q4_pct = (q4_rev / tot_rev * 100) if tot_rev > 0 else 0
            quarters_present = sorted(work_df["quarter"].unique().tolist())
            q4_warning = (f"No Q4 records in dataset (data covers quarters {quarters_present} only) "
                          f"— this reflects missing data, not an actual seasonal decline") if not q4_mask.any() else "None"
            kpis.append(engine.build_kpi("📅 Seasonality", "Q4 Contribution", f"{q4_pct:.2f}%", "Q4 / Total * 100", f"`{rev_col}`, `{date_col}`", warnings=q4_warning))
            
            var = work_df[rev_col].std() / work_df[rev_col].mean() if work_df[rev_col].mean() > 0 else 0
            kpis.append(engine.build_kpi("📅 Seasonality", "Demand Variability", f"{var:.3f}", "StdDev/Mean", f"`{rev_col}`", warnings="High variability" if var > 0.5 else "None"))
            
            mo_ordered = work_df.set_index(date_col)[rev_col].resample("ME").sum()
            if len(mo_ordered) >= 2 and mo_ordered.iloc[0] != 0:
                s_growth = ((mo_ordered.iloc[-1] - mo_ordered.iloc[0]) / mo_ordered.iloc[0]) * 100
                kpis.append(engine.build_kpi("📅 Seasonality", "Seasonal Growth %", f"{s_growth:.2f}%", "Last Month vs First Month", f"`{rev_col}`, `{date_col}`"))
    else:
        kpis.append(engine.log_missing("📅 Seasonality", "Seasonality Metrics", "Requires 'date' and numeric 'revenue'."))

    if hol_col is not None and rev_col is not None:
        hol_df = pd.concat([hol_series, rev_series], axis=1).dropna()
        if len(hol_df) > 0:
            mask = hol_df[hol_col].astype(str).str.lower().isin(['true', '1', 'yes', 'y'])
            if mask.any() and (~mask).any():
                hol_avg = hol_df.loc[mask, rev_col].mean()
                non_hol_avg = hol_df.loc[~mask, rev_col].mean()
                uplift = ((hol_avg - non_hol_avg) / non_hol_avg * 100) if non_hol_avg > 0 else 0
                kpis.append(engine.build_kpi("📅 Seasonality", "Holiday Sales Uplift", f"{uplift:.2f}%", "(Holiday Avg - Non-Holiday Avg) / Non-Holiday Avg * 100", f"`{hol_col}`, `{rev_col}`"))

    if enable_debug: engine.print_execution_log()
    return kpis
