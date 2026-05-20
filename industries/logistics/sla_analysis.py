import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_sla_performance(df):
    kpis = []
    if len(df) == 0: return kpis

    status_col = _first_column(df, ['delivery_status', 'sla_status', 'on_time_status'])
    
    if not status_col: 
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [status_col])
    
    status_str = df[status_col].astype(str).str.lower()
    on_time = status_str.str.contains("on time|completed|success", na=False).sum()
    on_time_rate = (on_time / len(df)) * 100

    kpis.append({
        "category": "⏱️ SLA Performance",
        "name": "On-Time Delivery Rate",
        "value": f"{on_time_rate:.2f}%",
        "formula": "(COUNT(On Time) / TOTAL) * 100",
        "source": f"`{status_col}`",
        "confidence": conf,
        "warnings": "Critical SLA breaches detected" if on_time_rate < 90 else warns
    })

    return kpis
