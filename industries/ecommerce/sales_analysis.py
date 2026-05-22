import pandas as pd
from .common import confidence_for, excluded_kpi, first_column, safe_kpi
from utils.validator import SemanticValidator


def calc_sales_metrics(df):
    kpis = []
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "total_sales", "gmv"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "timestamp"])
    if not revenue_col:
        return kpis

    is_valid, reason = SemanticValidator.is_valid_duration(df[revenue_col])
    if not is_valid:
        return [excluded_kpi("🛒 Sales Analysis", "Sales Metrics", f"`{revenue_col}`", reason)]

    valid_revenue = df[revenue_col].dropna()
    if valid_revenue.empty:
        return kpis

    conf, warns = confidence_for(df, [revenue_col, date_col] if date_col else [revenue_col])
    kpis.append(safe_kpi("🛒 Sales Analysis", "Total Revenue", f"${valid_revenue.sum():,.2f}", "Sum(revenue)", f"`{revenue_col}`", conf, warns))
    kpis.append(safe_kpi("🛒 Sales Analysis", "Avg Order Value", f"${valid_revenue.mean():,.2f}", "Mean(order value)", f"`{revenue_col}`", conf, warns))
    kpis.append(safe_kpi("🛒 Sales Analysis", "Median Order Value", f"${valid_revenue.median():,.2f}", "Median(order value)", f"`{revenue_col}`", conf, warns))
    kpis.append(safe_kpi("🛒 Sales Analysis", "Revenue Variance", f"{valid_revenue.var():,.2f}", "Var(order value)", f"`{revenue_col}`", conf, warns))

    if date_col:
        dt_series = pd.to_datetime(df[date_col], errors="coerce")
        dt_valid, dt_reason = SemanticValidator.is_valid_datetime(dt_series.dropna())
        if dt_valid and dt_series.notna().sum() > 1:
            trend_df = pd.DataFrame({"date": dt_series, "revenue": df[revenue_col]}).dropna()
            monthly = trend_df.set_index("date")["revenue"].resample("M").sum().dropna()
            if not monthly.empty:
                first_period = monthly.iloc[0]
                last_period = monthly.iloc[-1]
                growth = ((last_period - first_period) / first_period) * 100 if first_period != 0 else 0
                peak_period = monthly.idxmax().strftime("%Y-%m-%d")
                rolling_avg = monthly.rolling(window=3, min_periods=1).mean().iloc[-1]
                kpis.append(safe_kpi("🛒 Sales Analysis", "Revenue Growth %", f"{growth:.2f}%", "((Last - First) / First) * 100", f"`{revenue_col}`, `{date_col}`", conf, warns))
                kpis.append(safe_kpi("🛒 Sales Analysis", "Peak Revenue Period", peak_period, "ArgMax(Monthly Revenue)", f"`{revenue_col}`, `{date_col}`", conf, warns))
                kpis.append(safe_kpi("🛒 Sales Analysis", "3-Period Moving Average", f"${rolling_avg:,.2f}", "RollingMean(Monthly Revenue, 3)", f"`{revenue_col}`, `{date_col}`", conf, warns))
        else:
            kpis.append(excluded_kpi("🛒 Sales Analysis", "Trend Metrics", f"`{date_col}`", dt_reason))

    return kpis
