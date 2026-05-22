import pandas as pd
from utils.validator import SemanticValidator
from .reliability import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_maintenance_metrics(df):
    """Compute maintenance performance KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    mtbf_col = _first_column(df, ["mtbf_hours", "mean_time_between_failures"])
    mttr_col = _first_column(df, ["mttr_hours", "mean_time_to_repair"])
    pm_col = _first_column(df, ["preventive_maintenance_hours", "planned_maintenance_hours"])

    if mtbf_col and pd.api.types.is_numeric_dtype(df[mtbf_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [mtbf_col])
        kpis.append({
            "category": "🛠️ Maintenance",
            "name": "Average MTBF",
            "value": f"{df[mtbf_col].mean():,.1f} hours",
            "formula": f"AVG({mtbf_col})",
            "source": mtbf_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if mttr_col and pd.api.types.is_numeric_dtype(df[mttr_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [mttr_col])
        kpis.append({
            "category": "🛠️ Maintenance",
            "name": "Average MTTR",
            "value": f"{df[mttr_col].mean():,.1f} hours",
            "formula": f"AVG({mttr_col})",
            "source": mttr_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if pm_col and pd.api.types.is_numeric_dtype(df[pm_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [pm_col])
        kpis.append({
            "category": "🛠️ Maintenance",
            "name": "Preventive Maintenance Hours",
            "value": f"{df[pm_col].sum():,.1f} hours",
            "formula": f"SUM({pm_col})",
            "source": pm_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
