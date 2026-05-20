import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_adverse_events_metrics(df):
    """Computes pharmacovigilance and adverse event signal detection KPIs."""
    kpis = []
    if len(df) == 0: return kpis

    sae_col = _first_column(df, ["sae_count", "serious_adverse_events"])
    severity_col = _first_column(df, ["severity", "event_severity", "grade"])

    if not sae_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    sae_valid, reason = SemanticValidator.is_valid_duration(df[sae_col].fillna(0))
    if not sae_valid:
        return [{
            "category": "⚠️ Pharmacovigilance", "name": "Serious Adverse Events",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{sae_col}`",
            "confidence": "Low", "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [sae_col])
    total_sae = df[sae_col].fillna(0).sum()
    
    kpis.append({
        "category": "⚠️ Pharmacovigilance",
        "name": "Total Serious Adverse Events (SAE)",
        "value": f"{total_sae:,.0f}",
        "formula": "SUM(sae_count)",
        "source": f"`{sae_col}`",
        "confidence": conf,
        "warnings": "High volume of SAEs detected" if total_sae > 50 else warns
    })

    if severity_col:
        severe_events = df[severity_col].astype(str).str.lower().str.contains("severe|grade 3|grade 4|life-threatening", na=False).sum()
        severe_ratio = (severe_events / len(df)) * 100
        kpis.append({
            "category": "⚠️ Pharmacovigilance",
            "name": "Severe Event Ratio (Grade 3/4)",
            "value": f"{severe_ratio:.2f}%",
            "formula": "(COUNT(Severe) / TOTAL) * 100",
            "source": f"`{severity_col}`",
            "confidence": conf,
            "warnings": "Elevated severity signal" if severe_ratio > 10 else warns
        })

    return kpis
