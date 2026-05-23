import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_cost_metrics(df):
    """Compute manufacturing cost KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis
    cost_col = _first_column(df, ["total_cost", "operating_cost", "ProductionCost", "AdditiveMaterialCost"])
    unit_cost_col = _first_column(df, ["unit_cost", "cost_per_unit"])
    scrap_cost_col = _first_column(df, ["scrap_cost", "waste_cost"])

    if cost_col and pd.api.types.is_numeric_dtype(df[cost_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [cost_col])
        kpis.append({
            "category": "💲 Cost",
            "name": "Total Manufacturing Cost",
            "value": f"${df[cost_col].sum():,.2f}",
            "formula": f"SUM({cost_col})",
            "source": cost_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if unit_cost_col and pd.api.types.is_numeric_dtype(df[unit_cost_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [unit_cost_col])
        kpis.append({
            "category": "💲 Cost",
            "name": "Average Unit Cost",
            "value": f"${df[unit_cost_col].mean():,.2f}",
            "formula": f"AVG({unit_cost_col})",
            "source": unit_cost_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if scrap_cost_col and pd.api.types.is_numeric_dtype(df[scrap_cost_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [scrap_cost_col])
        kpis.append({
            "category": "💲 Cost",
            "name": "Total Scrap Cost",
            "value": f"${df[scrap_cost_col].sum():,.2f}",
            "formula": f"SUM({scrap_cost_col})",
            "source": scrap_cost_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
