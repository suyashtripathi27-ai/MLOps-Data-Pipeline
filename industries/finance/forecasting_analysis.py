"""Forecasting helpers: simple growth projections and seasonality hints."""
import pandas as pd
from .reliability import evaluate_kpi_confidence


def _first_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def calc_forecasting_metrics(df):
    kpis = []
    revenue_col = _first_column(df, ["revenue", "sales", "turnover"]) 
    date_col = _first_column(df, ["date", "transaction_date", "period"])

    if not revenue_col or not date_col:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [revenue_col, date_col])
    try:
        dfc = df.copy()
        dfc["_d"] = pd.to_datetime(dfc[date_col], errors="coerce")
        monthly = dfc.dropna(subset=["_d"]).set_index("_d").resample('M')[revenue_col].sum()
        if len(monthly) >= 6:
            recent_growth = monthly.pct_change().dropna().iloc[-3:].mean()
            kpis.append({
                "category": "🔮 Forecasting",
                "name": "Recent 3-Month Avg Growth",
                "value": f"{recent_growth:.2%}",
                "formula": "Mean(Pct Change, Last 3 Months)",
                "source": f"`{date_col}`, `{revenue_col}`",
                "confidence": conf,
                "warnings": warns,
            })
            # seasonality hint: month with highest average
            monthly_group = monthly.groupby(monthly.index.month).mean()
            top_month = monthly_group.idxmax()
            kpis.append({
                "category": "🔮 Forecasting",
                "name": "Strongest Month (Avg)",
                "value": f"Month {int(top_month)}",
                "formula": "Month with highest avg revenue",
                "source": f"`{date_col}`, `{revenue_col}`",
                "confidence": conf,
                "warnings": warns,
            })
    except Exception:
        pass

    return kpis
