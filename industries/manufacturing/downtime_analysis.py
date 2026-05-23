import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_downtime_metrics(df):
    """Compute planned and unplanned downtime KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    downtime_col = _first_column(df, ["downtime_hours", "unplanned_downtime", "machine_downtime_hours"])
    if downtime_col and pd.api.types.is_numeric_dtype(df[downtime_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [downtime_col])
        kpis.append({
            "category": "⏱️ Downtime",
            "name": "Total Downtime Hours",
            "value": f"{df[downtime_col].sum():,.1f} hours",
            "formula": f"SUM({downtime_col})",
            "source": downtime_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
