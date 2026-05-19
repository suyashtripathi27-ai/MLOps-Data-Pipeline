import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_seasonality_metrics(df):
    """Calculates holiday uplift and seasonal contribution KPIs."""
    kpis = []
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    date_col = _first_column(df, ["date", "transaction_date", "order_date", "week_date", "timestamp"])
    holiday_col = _first_column(df, ["is_holiday", "holiday_flag", "holiday"])
    if not revenue_col or not date_col:
        return kpis

    rev_valid, reason = SemanticValidator.is_valid_duration(df[revenue_col])
    if not rev_valid:
        return [{
            "category": "📅 Seasonality Analysis",
            "name": "Seasonality Metrics",
            "value": "EXCLUDED",
            "formula": "N/A",
            "source": f"`{revenue_col}`, `{date_col}`",
            "confidence": "Low",
            "warnings": reason
        }]

    work_df = df[[revenue_col]].copy()
    work_df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    work_df = work_df.dropna(subset=["date", revenue_col])
    if work_df.empty:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [revenue_col, date_col])
    work_df["month"] = work_df["date"].dt.month
    work_df["quarter"] = work_df["date"].dt.quarter
    monthly = work_df.groupby("month")[revenue_col].sum()
    peak_month = int(monthly.idxmax()) if not monthly.empty else 0
    q4_share = (work_df.loc[work_df["quarter"] == 4, revenue_col].sum() / work_df[revenue_col].sum() * 100) if work_df[revenue_col].sum() > 0 else 0
    demand_variability = work_df[revenue_col].std(ddof=0) / work_df[revenue_col].mean() if work_df[revenue_col].mean() else 0

    kpis.append({
        "category": "📅 Seasonality Analysis",
        "name": "Peak Sales Month",
        "value": f"Month {peak_month}",
        "formula": "ArgMax(Monthly Revenue)",
        "source": f"`{revenue_col}`, `{date_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "📅 Seasonality Analysis",
        "name": "Q4 Contribution",
        "value": f"{q4_share:.2f}%",
        "formula": "Q4 Revenue / Total Revenue * 100",
        "source": f"`{revenue_col}`, `{date_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "📅 Seasonality Analysis",
        "name": "Demand Variability",
        "value": f"{demand_variability:.3f}",
        "formula": "StdDev(Revenue) / Mean(Revenue)",
        "source": f"`{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    monthly_ordered = work_df.set_index("date")[revenue_col].resample("M").sum()
    if len(monthly_ordered) >= 2 and monthly_ordered.iloc[0] != 0:
        seasonal_growth = ((monthly_ordered.iloc[-1] - monthly_ordered.iloc[0]) / monthly_ordered.iloc[0]) * 100
        kpis.append({
            "category": "📅 Seasonality Analysis",
            "name": "Seasonal Growth",
            "value": f"{seasonal_growth:.2f}%",
            "formula": "((Last Month - First Month) / First Month) * 100",
            "source": f"`{revenue_col}`, `{date_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if holiday_col:
        holiday_series = df[holiday_col].astype(str).str.lower().isin(["true", "1", "yes", "y"])
        holiday_df = pd.DataFrame({
            "is_holiday": holiday_series,
            "revenue": df[revenue_col],
        }).dropna()
        if holiday_df["is_holiday"].any() and (~holiday_df["is_holiday"]).any():
            holiday_avg = holiday_df.loc[holiday_df["is_holiday"], "revenue"].mean()
            non_holiday_avg = holiday_df.loc[~holiday_df["is_holiday"], "revenue"].mean()
            uplift = ((holiday_avg - non_holiday_avg) / non_holiday_avg * 100) if non_holiday_avg else 0
            kpis.append({
                "category": "📅 Seasonality Analysis",
                "name": "Holiday Sales Uplift",
                "value": f"{uplift:.2f}%",
                "formula": "((Holiday Avg - Non-Holiday Avg) / Non-Holiday Avg) * 100",
                "source": f"`{holiday_col}`, `{revenue_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    return kpis
