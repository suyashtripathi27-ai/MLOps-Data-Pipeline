import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def calc_production_metrics(df):
    """Compute core plant production KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    produced_col = first_column(df, ["production_volume", "actual_output", "units_produced", "output_units", "good_units"])
    planned_col = first_column(df, ["planned_output", "target_output", "production_target", "expected_output"])
    downtime_col = first_column(df, ["downtime_hours", "unplanned_downtime", "machine_downtime_hours"])

    if produced_col and pd.api.types.is_numeric_dtype(df[produced_col]):
        produced_total = df[produced_col].sum()
        confidence, warnings = evaluate_kpi_confidence(df, [produced_col])
        kpis.append({
            "category": "🏭 Production",
            "name": "Total Output",
            "value": f"{produced_total:,.0f} units",
            "formula": f"SUM({produced_col})",
            "source": produced_col,
            "confidence": confidence,
            "warnings": warnings,
        })

        if planned_col and pd.api.types.is_numeric_dtype(df[planned_col]):
            planned_total = df[planned_col].sum()
            attainment = (produced_total / planned_total * 100) if planned_total else 0
            confidence, warnings = evaluate_kpi_confidence(df, [produced_col, planned_col])
            kpis.append({
                "category": "🏭 Production",
                "name": "Plan Attainment",
                "value": f"{attainment:,.1f}%",
                "formula": f"SUM({produced_col}) / SUM({planned_col})",
                "source": f"{produced_col}, {planned_col}",
                "confidence": confidence,
                "warnings": warnings if warnings != "None" else ("Below target" if attainment < 95 else "None"),
            })

    if downtime_col and pd.api.types.is_numeric_dtype(df[downtime_col]):
        downtime_total = df[downtime_col].sum()
        confidence, warnings = evaluate_kpi_confidence(df, [downtime_col])
        kpis.append({
            "category": "🏭 Production",
            "name": "Total Downtime",
            "value": f"{downtime_total:,.1f} hours",
            "formula": f"SUM({downtime_col})",
            "source": downtime_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
