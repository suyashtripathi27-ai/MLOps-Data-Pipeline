import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_efficiency_metrics(df):
    """Compute manufacturing efficiency KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    efficiency_col = _first_column(df, ["efficiency", "overall_efficiency", "line_efficiency"])
    oee_col = _first_column(df, ["oee", "overall_equipment_effectiveness"])
    utilization_col = _first_column(df, ["utilization_rate", "capacity_utilization"])

    if efficiency_col and pd.api.types.is_numeric_dtype(df[efficiency_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [efficiency_col])
        kpis.append({
            "category": "⚙️ Efficiency",
            "name": "Average Efficiency",
            "value": f"{df[efficiency_col].mean():,.2f}%",
            "formula": f"AVG({efficiency_col})",
            "source": efficiency_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if oee_col and pd.api.types.is_numeric_dtype(df[oee_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [oee_col])
        kpis.append({
            "category": "⚙️ Efficiency",
            "name": "Average OEE",
            "value": f"{df[oee_col].mean():,.2f}%",
            "formula": f"AVG({oee_col})",
            "source": oee_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if utilization_col and pd.api.types.is_numeric_dtype(df[utilization_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [utilization_col])
        kpis.append({
            "category": "⚙️ Efficiency",
            "name": "Capacity Utilization",
            "value": f"{df[utilization_col].mean():,.2f}%",
            "formula": f"AVG({utilization_col})",
            "source": utilization_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
