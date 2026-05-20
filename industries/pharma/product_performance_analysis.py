import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_product_performance_metrics(df):
    """Computes commercial product performance and market complaint rates."""
    kpis = []
    if len(df) == 0: return kpis

    complaint_col = _first_column(df, ["complaints", "complaint_count", "adverse_reports"])
    sales_col = _first_column(df, ["quantity_sold", "units_dispensed", "actual_demand"])

    if not sales_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    sales_valid, reason = SemanticValidator.is_valid_duration(df[sales_col].fillna(0))
    if not sales_valid:
        return [{
            "category": "💊 Product Performance", "name": "Commercial Performance",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{sales_col}`",
            "confidence": "Low", "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [sales_col, complaint_col])
    total_sold = df[sales_col].fillna(0).sum()

    kpis.append({
        "category": "💊 Product Performance",
        "name": "Total Commercial Units Dispensed",
        "value": f"{total_sold:,.0f}",
        "formula": "SUM(quantity_sold)",
        "source": f"`{sales_col}`",
        "confidence": conf,
        "warnings": warns
    })

    if complaint_col and total_sold > 0:
        total_complaints = df[complaint_col].fillna(0).sum()
        complaint_rate = (total_complaints / total_sold) * 100
        
        kpis.append({
            "category": "💊 Product Performance",
            "name": "Market Complaint Rate",
            "value": f"{complaint_rate:.4f}%",
            "formula": "(SUM(complaints) / SUM(quantity_sold)) * 100",
            "source": f"`{complaint_col}`, `{sales_col}`",
            "confidence": conf,
            "warnings": "Market complaint rate exceeds standard thresholds" if complaint_rate > 0.05 else warns
        })

    return kpis
