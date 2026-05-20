import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator  # 🛡️ THE CENTRAL VALIDATOR

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_manufacturing_metrics(df):
    """Computes manufacturing efficiency and deviation KPIs."""
    kpis = []
    total_rows = len(df)
    if total_rows == 0: return kpis

    yield_col = _first_column(df, ["batch_yield", "yield_percentage", "production_yield"])
    oos_col = _first_column(df, ["oos_rate", "out_of_spec_rate", "oos_count"])

    if not yield_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    yield_valid, reason = SemanticValidator.is_valid_duration(df[yield_col].fillna(0))
    if not yield_valid:
        return [{
            "category": "🏭 Manufacturing", "name": "Batch Yield",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{yield_col}`",
            "confidence": "Low", "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [yield_col, oos_col])
    
    avg_yield = df[yield_col].dropna().mean()
    kpis.append({
        "category": "🏭 Manufacturing",
        "name": "Average Batch Yield",
        "value": f"{avg_yield:.2f}%",
        "formula": "AVG(batch_yield)",
        "source": f"`{yield_col}`",
        "confidence": conf,
        "warnings": "Suboptimal production yield" if avg_yield < 85 else warns
    })

    if oos_col:
        avg_oos = df[oos_col].dropna().mean()
        if avg_oos > 1: avg_oos = (df[oos_col].sum() / total_rows) * 100 
        
        kpis.append({
            "category": "🏭 Manufacturing",
            "name": "Out of Specification (OOS) Rate",
            "value": f"{avg_oos:.2f}%",
            "formula": "AVG(oos_rate)",
            "source": f"`{oos_col}`",
            "confidence": conf,
            "warnings": "Critical OOS levels" if avg_oos > 5 else warns
        })

    return kpis
