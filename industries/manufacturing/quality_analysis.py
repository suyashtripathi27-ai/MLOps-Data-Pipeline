import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def calc_quality_metrics(df):
    """Compute core manufacturing quality KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis
    quality_col = first_column(df, ["supplier_quality", "vendor_rating", "SupplierQuality"])
    good_col = first_column(df, ["good_units", "accepted_units", "pass_units", "saleable_units"])
    scrap_col = first_column(df, ["scrap_units", "reject_units", "defective_units", "waste_units"])
    defect_col = first_column(df, ["defect_rate", "scrap_rate", "reject_rate"])

    if good_col and pd.api.types.is_numeric_dtype(df[good_col]):
        good_total = df[good_col].sum()
        confidence, warnings = evaluate_kpi_confidence(df, [good_col])
        kpis.append({
            "category": "🔬 Quality",
            "name": "Saleable Output",
            "value": f"{good_total:,.0f} units",
            "formula": f"SUM({good_col})",
            "source": good_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if scrap_col and pd.api.types.is_numeric_dtype(df[scrap_col]):
        scrap_total = df[scrap_col].sum()
        confidence, warnings = evaluate_kpi_confidence(df, [scrap_col])
        kpis.append({
            "category": "🔬 Quality",
            "name": "Scrap / Reject Volume",
            "value": f"{scrap_total:,.0f} units",
            "formula": f"SUM({scrap_col})",
            "source": scrap_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if defect_col and pd.api.types.is_numeric_dtype(df[defect_col]):
        defect_avg = df[defect_col].mean()
        confidence, warnings = evaluate_kpi_confidence(df, [defect_col])
        kpis.append({
            "category": "🔬 Quality",
            "name": "Average Defect Rate",
            "value": f"{defect_avg:,.2f}%",
            "formula": f"AVG({defect_col})",
            "source": defect_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
