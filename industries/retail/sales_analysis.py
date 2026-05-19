import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _safe_kpi(name, value, formula, source, confidence, warnings):
    return {
        "category": "💰 Sales Analysis",
        "name": name,
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warnings": warnings,
    }


def calc_sales_metrics(df):
    """Calculates retail sales KPIs, trend metrics, and demand spikes."""
    kpis = []
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    date_col = _first_column(df, ["date", "transaction_date", "order_date", "week_date", "timestamp"])

    if not revenue_col:
        return kpis

    is_valid, reason = SemanticValidator.is_valid_duration(df[revenue_col])
    if not is_valid:
        kpis.append(_safe_kpi("Sales Metrics", "EXCLUDED", "N/A", f"`{revenue_col}`", "Low", reason))
        return kpis

    valid_revenue = df[revenue_col].dropna()
    if valid_revenue.empty:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [revenue_col])
    kpis.append(_safe_kpi("Total Revenue", f"${valid_revenue.sum():,.2f}", "Sum(revenue)", f"`{revenue_col}`", conf, warns))
    kpis.append(_safe_kpi("Avg Weekly Sales", f"${valid_revenue.mean():,.2f}", "Mean(revenue)", f"`{revenue_col}`", conf, warns))
    kpis.append(_safe_kpi("Median Sales", f"${valid_revenue.median():,.2f}", "Median(revenue)", f"`{revenue_col}`", conf, warns))
    kpis.append(_safe_kpi("Sales Variance", f"{valid_revenue.var():,.2f}", "Var(revenue)", f"`{revenue_col}`", conf, warns))

    if date_col:
        dt_series = pd.to_datetime(df[date_col], errors="coerce")
        dt_valid, dt_reason = SemanticValidator.is_valid_datetime(dt_series.dropna())
        if dt_valid and dt_series.notna().sum() > 1:
            trend_df = pd.DataFrame({"date": dt_series, "revenue": df[revenue_col]}).dropna()
            weekly = trend_df.set_index("date")["revenue"].resample("W").sum().dropna()
            if not weekly.empty:
                first_week = weekly.iloc[0]
                last_week = weekly.iloc[-1]
                growth = ((last_week - first_week) / first_week) * 100 if first_week != 0 else 0
                top_period = weekly.idxmax().strftime("%Y-%m-%d")
                moving_avg = weekly.rolling(window=4, min_periods=1).mean().iloc[-1]
                spike_threshold = weekly.mean() + (2 * weekly.std(ddof=0))
                demand_spikes = int((weekly > spike_threshold).sum()) if pd.notnull(spike_threshold) else 0
                conf_trend, warns_trend = evaluate_kpi_confidence(df, [revenue_col, date_col])
                kpis.append(_safe_kpi("Revenue Growth %", f"{growth:.2f}%", "((Last - First) / First) * 100", f"`{revenue_col}`, `{date_col}`", conf_trend, warns_trend))
                kpis.append(_safe_kpi("Top Revenue Period", top_period, "ArgMax(Weekly Revenue)", f"`{revenue_col}`, `{date_col}`", conf_trend, warns_trend))
                kpis.append(_safe_kpi("4-Week Moving Average", f"${moving_avg:,.2f}", "RollingMean(Weekly Revenue, 4)", f"`{revenue_col}`, `{date_col}`", conf_trend, warns_trend))
                kpis.append(_safe_kpi("Demand Spikes", f"{demand_spikes}", "Count(Weekly Revenue > Mean + 2*Std)", f"`{revenue_col}`, `{date_col}`", conf_trend, warns_trend))
        else:
            kpis.append(_safe_kpi("Trend Metrics", "EXCLUDED", "N/A", f"`{date_col}`", "Low", dt_reason))

    return kpis
