import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_inventory_metrics(df):
    """Compute inventory and WIP related manufacturing KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis
    turnover_col = _first_column(df, ["inventory_turnover", "turnover_rate", "InventoryTurnover"])
    stockout_col = _first_column(df, ["stockouts", "stockout_rate", "StockoutRate"])
    inventory_col = _first_column(df, ["inventory_level", "stock_on_hand", "raw_material_stock", "wip_units"])
    shortage_col = _first_column(df, ["stockout_count", "shortage_units", "material_shortage"])
    aging_col = _first_column(df, ["inventory_age_days", "wip_age_days", "aging_days"])

    if inventory_col and pd.api.types.is_numeric_dtype(df[inventory_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [inventory_col])
        kpis.append({
            "category": "📦 Inventory",
            "name": "Average Inventory Level",
            "value": f"{df[inventory_col].mean():,.1f}",
            "formula": f"AVG({inventory_col})",
            "source": inventory_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if shortage_col and pd.api.types.is_numeric_dtype(df[shortage_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [shortage_col])
        kpis.append({
            "category": "📦 Inventory",
            "name": "Stockout / Shortage Count",
            "value": f"{df[shortage_col].sum():,.0f}",
            "formula": f"SUM({shortage_col})",
            "source": shortage_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if aging_col and pd.api.types.is_numeric_dtype(df[aging_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [aging_col])
        kpis.append({
            "category": "📦 Inventory",
            "name": "Average Inventory Age",
            "value": f"{df[aging_col].mean():,.1f} days",
            "formula": f"AVG({aging_col})",
            "source": aging_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
