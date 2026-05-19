import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_store_metrics(df):
    """Calculates store performance and concentration KPIs."""
    kpis = []
    store_col = _first_column(df, ["store_id", "store", "store_name", "outlet_id"])
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    date_col = _first_column(df, ["date", "transaction_date", "order_date", "week_date"])
    if not store_col or not revenue_col:
        return kpis

    rev_valid, reason = SemanticValidator.is_valid_duration(df[revenue_col])
    if not rev_valid:
        return [{
            "category": "🏬 Store Analysis",
            "name": "Store Metrics",
            "value": "EXCLUDED",
            "formula": "N/A",
            "source": f"`{store_col}`, `{revenue_col}`",
            "confidence": "Low",
            "warnings": reason
        }]

    valid_df = df[[store_col, revenue_col]].dropna()
    if valid_df.empty:
        return kpis

    store_rev = valid_df.groupby(store_col)[revenue_col].sum().sort_values(ascending=False)
    conf, warns = evaluate_kpi_confidence(df, [store_col, revenue_col])
    kpis.append({
        "category": "🏬 Store Analysis",
        "name": "Revenue per Store",
        "value": f"${store_rev.mean():,.2f}",
        "formula": "Mean(Store Revenue)",
        "source": f"`{store_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "🏬 Store Analysis",
        "name": "Avg Sales per Store",
        "value": f"${(valid_df[revenue_col].mean()):,.2f}",
        "formula": "Mean(Transaction Revenue)",
        "source": f"`{store_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    top10_contrib = ((store_rev.head(10).sum() / store_rev.sum()) * 100) if store_rev.sum() > 0 else 0
    weakest_store = store_rev.idxmin()
    weakest_store_rev = store_rev.min()
    kpis.append({
        "category": "🏬 Store Analysis",
        "name": "Top 10 Store Contribution",
        "value": f"{top10_contrib:.2f}%",
        "formula": "Top10 Store Revenue / Total Revenue * 100",
        "source": f"`{store_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "🏬 Store Analysis",
        "name": "Weakest Store",
        "value": f"{weakest_store} (${weakest_store_rev:,.2f})",
        "formula": "Store with minimum total revenue",
        "source": f"`{store_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if date_col:
        date_series = pd.to_datetime(df[date_col], errors="coerce")
        date_valid, _ = SemanticValidator.is_valid_datetime(date_series.dropna())
        if date_valid:
            growth_df = df[[store_col, revenue_col]].copy()
            growth_df["date"] = date_series
            growth_df = growth_df.dropna(subset=["date"])
            if not growth_df.empty:
                by_store_month = growth_df.groupby([store_col, pd.Grouper(key="date", freq="M")])[revenue_col].sum()
                growth_rates = []
                for _, s in by_store_month.groupby(level=0):
                    values = s.values
                    if len(values) >= 2 and values[0] != 0:
                        growth_rates.append(((values[-1] - values[0]) / values[0]) * 100)
                if growth_rates:
                    kpis.append({
                        "category": "🏬 Store Analysis",
                        "name": "Store Growth Rate",
                        "value": f"{pd.Series(growth_rates).mean():.2f}%",
                        "formula": "Average store growth from first to last period",
                        "source": f"`{store_col}`, `{revenue_col}`, `{date_col}`",
                        "confidence": conf,
                        "warnings": warns,
                    })

    return kpis
