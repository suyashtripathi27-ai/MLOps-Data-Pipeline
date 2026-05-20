import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator  # 🛡️ THE CENTRAL VALIDATOR IS BACK

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_clinical_metrics(df):
    """Computes clinical trial enrollment and retention KPIs."""
    kpis = []
    total_rows = len(df)
    if total_rows == 0: return kpis

    enrolled_col = _first_column(df, ["enrolled", "participants", "enrollment_count"])
    dropout_col = _first_column(df, ["dropouts", "dropout_count", "withdrawn"])

    if not enrolled_col or not dropout_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION: Check if the data is fundamentally broken
    enrolled_valid, reason = SemanticValidator.is_valid_duration(df[enrolled_col].fillna(0))
    if not enrolled_valid:
        return [{
            "category": "🧪 Clinical Trials", "name": "Trial Enrollment",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{enrolled_col}`",
            "confidence": "Low", "warnings": reason
        }]

    # 🧮 If valid, proceed with the math!
    conf, warns = evaluate_kpi_confidence(df, [enrolled_col, dropout_col])
    
    total_enrolled = df[enrolled_col].fillna(0).sum()
    total_dropouts = df[dropout_col].fillna(0).sum()
    dropout_rate = (total_dropouts / total_enrolled * 100) if total_enrolled > 0 else 0

    kpis.append({
        "category": "🧪 Clinical Trials",
        "name": "Total Enrolled Patients",
        "value": f"{total_enrolled:,.0f}",
        "formula": "SUM(enrolled)",
        "source": f"`{enrolled_col}`",
        "confidence": conf,
        "warnings": warns
    })

    kpis.append({
        "category": "🧪 Clinical Trials",
        "name": "Clinical Dropout Rate",
        "value": f"{dropout_rate:.2f}%",
        "formula": "(Dropouts / Enrolled) * 100",
        "source": f"`{dropout_col}`, `{enrolled_col}`",
        "confidence": conf,
        "warnings": "Critical retention risk" if dropout_rate > 15 else warns
    })

    return kpis
