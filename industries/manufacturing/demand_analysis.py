import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_demand_metrics(df):
    """Compute demand and order signal KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    demand_col = _first_column(df, ["demand_units", "market_demand", "orders"])
    backlog_col = _first_column(df, ["backlog_units", "open_orders", "unfulfilled_demand"])
    order_fill_col = _first_column(df, ["order_fill_rate", "fill_rate"])

    if demand_col and pd.api.types.is_numeric_dtype(df[demand_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [demand_col])
        kpis.append({
            "category": "🧭 Demand",
            "name": "Total Demand",
            "value": f"{df[demand_col].sum():,.0f} units",
            "formula": f"SUM({demand_col})",
            "source": demand_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if backlog_col and pd.api.types.is_numeric_dtype(df[backlog_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [backlog_col])
        kpis.append({
            "category": "🧭 Demand",
            "name": "Backlog Volume",
            "value": f"{df[backlog_col].sum():,.0f} units",
            "formula": f"SUM({backlog_col})",
            "source": backlog_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if order_fill_col and pd.api.types.is_numeric_dtype(df[order_fill_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [order_fill_col])
        kpis.append({
            "category": "🧭 Demand",
            "name": "Average Order Fill Rate",
            "value": f"{df[order_fill_col].mean():,.2f}%",
            "formula": f"AVG({order_fill_col})",
            "source": order_fill_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
