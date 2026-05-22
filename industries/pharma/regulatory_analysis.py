import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_regulatory_metrics(df):
    """Computes FDA/EMA submission lead times and compliance status."""
    kpis = []
    total_rows = len(df)
    if total_rows == 0: return kpis

    sub_col = _first_column(df, ["submission_date", "nda_submission"])
    app_col = _first_column(df, ["approval_date", "fda_approval"])
    status_col = _first_column(df, ["regulatory_status", "compliance_status"])

    # For dates, we validate by checking if Pandas can successfully parse them
    if sub_col and app_col:
        conf, warns = evaluate_kpi_confidence(df, [sub_col, app_col])
        sub_dates = pd.to_datetime(df[sub_col], errors='coerce')
        app_dates = pd.to_datetime(df[app_col], errors='coerce')
        
        valid_dates = sub_dates.notna() & app_dates.notna()
        if valid_dates.any():
            lead_times = (app_dates[valid_dates] - sub_dates[valid_dates]).dt.days
            avg_approval = lead_times.mean()

            kpis.append({
                "category": "⚖️ Regulatory Affairs",
                "name": "Avg FDA/EMA Approval Lead Time",
                "value": f"{avg_approval:.0f} days",
                "formula": "AVG(approval_date - submission_date)",
                "source": f"`{sub_col}`, `{app_col}`",
                "confidence": conf,
                "warnings": "Approval timelines exceeding 365 days" if avg_approval > 365 else warns
            })
        else:
            kpis.append({
                "category": "⚖️ Regulatory Affairs", "name": "Avg FDA/EMA Approval Lead Time",
                "value": "EXCLUDED", "formula": "N/A", "source": f"`{sub_col}`, `{app_col}`",
                "confidence": "Low", "warnings": "Unparseable date formats detected."
            })

    if status_col:
        holds = df[status_col].astype(str).str.lower().str.contains("hold|pending|rejected|flagged", na=False).sum()
        hold_rate = (holds / total_rows) * 100
        # If the regulatory status column exists, we evaluate confidence for it
        conf, warns = evaluate_kpi_confidence(df, [status_col])
        
        kpis.append({
            "category": "⚖️ Regulatory Affairs",
            "name": "Regulatory Hold / Rejection Rate",
            "value": f"{hold_rate:.2f}%",
            "formula": "(COUNT(Holds) / TOTAL) * 100",
            "source": f"`{status_col}`",
            "confidence": conf,
            "warnings": "High regulatory friction detected" if hold_rate > 10 else warns
        })

    return kpis
