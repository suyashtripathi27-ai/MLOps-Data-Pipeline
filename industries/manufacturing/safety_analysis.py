import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def calc_safety_metrics(df):
    """Compute workplace safety KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    incident_col = first_column(df, ["incidents", "safety_incidents", "recordable_incidents"])
    near_miss_col = first_column(df, ["near_misses", "safety_near_misses"])
    lost_time_col = first_column(df, ["lost_time_injuries", "lti_count"])

    if incident_col and pd.api.types.is_numeric_dtype(df[incident_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [incident_col])
        kpis.append({
            "category": "🦺 Safety",
            "name": "Total Safety Incidents",
            "value": f"{df[incident_col].sum():,.0f}",
            "formula": f"SUM({incident_col})",
            "source": incident_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if near_miss_col and pd.api.types.is_numeric_dtype(df[near_miss_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [near_miss_col])
        kpis.append({
            "category": "🦺 Safety",
            "name": "Near Miss Count",
            "value": f"{df[near_miss_col].sum():,.0f}",
            "formula": f"SUM({near_miss_col})",
            "source": near_miss_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if lost_time_col and pd.api.types.is_numeric_dtype(df[lost_time_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [lost_time_col])
        kpis.append({
            "category": "🦺 Safety",
            "name": "Lost Time Injuries",
            "value": f"{df[lost_time_col].sum():,.0f}",
            "formula": f"SUM({lost_time_col})",
            "source": lost_time_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
