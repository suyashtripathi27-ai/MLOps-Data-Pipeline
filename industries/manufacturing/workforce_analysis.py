import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def calc_workforce_metrics(df):
    """Compute workforce productivity and staffing KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis
    labor_col = first_column(df, ["labor_hours", "operator_efficiency", "WorkerProductivity"])
    headcount_col = first_column(df, ["headcount", "employees", "workers", "shift_staff"])
    hours_col = first_column(df, ["labor_hours", "worked_hours", "shift_hours"])
    absenteeism_col = first_column(df, ["absenteeism_rate", "absence_rate"])

    if headcount_col and pd.api.types.is_numeric_dtype(df[headcount_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [headcount_col])
        kpis.append({
            "category": "👷 Workforce",
            "name": "Average Headcount",
            "value": f"{df[headcount_col].mean():,.1f}",
            "formula": f"AVG({headcount_col})",
            "source": headcount_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if hours_col and pd.api.types.is_numeric_dtype(df[hours_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [hours_col])
        kpis.append({
            "category": "👷 Workforce",
            "name": "Total Labor Hours",
            "value": f"{df[hours_col].sum():,.1f} hours",
            "formula": f"SUM({hours_col})",
            "source": hours_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if absenteeism_col and pd.api.types.is_numeric_dtype(df[absenteeism_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [absenteeism_col])
        kpis.append({
            "category": "👷 Workforce",
            "name": "Absenteeism Rate",
            "value": f"{df[absenteeism_col].mean():,.2f}%",
            "formula": f"AVG({absenteeism_col})",
            "source": absenteeism_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
