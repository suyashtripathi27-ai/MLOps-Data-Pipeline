import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def calc_compliance_metrics(df):
    """
    Scans for regulatory, FDA, EMA, or Quality Control (QC) compliance indicators.
    Gracefully bypasses if the dataset only contains sales data.
    """
    kpis = []
    if len(df) == 0: return kpis

    # 1. Detect compliance-related columns dynamically
    compliance_keywords = ['compliance', 'fda', 'ema', 'qc', 'quality', 'approved', 'status', 'recall', 'audit']
    compliance_cols = [c for c in df.columns if any(keyword in c.lower() for keyword in compliance_keywords)]

    if not compliance_cols:
        return kpis # Gracefully exit if this specific dataset doesn't have compliance data

    # 2. Calculate data confidence
    conf, warns = evaluate_kpi_confidence(df, compliance_cols)

    # 3. Tracked Compliance Volume
    kpis.append({
        "category": "⚖️ Regulatory Compliance",
        "name": "Audited / Tracked Records",
        "value": f"{len(df):,.0f}",
        "formula": "COUNT(Rows)",
        "source": f"Columns: {len(compliance_cols)}",
        "confidence": conf,
        "warnings": warns
    })

    # 4. Quality Control / Approval Rate
    status_col = next((c for c in compliance_cols if 'status' in c.lower() or 'approved' in c.lower() or 'qc' in c.lower()), None)

    if status_col:
        # Check for positive regulatory indicators
        passed = df[status_col].astype(str).str.lower().isin(['pass', 'approved', 'true', '1', 'yes', 'compliant', 'active']).sum()
        total = len(df[status_col].dropna())
        
        if total > 0:
            pass_rate = (passed / total) * 100
            kpis.append({
                "category": "⚖️ Regulatory Compliance",
                "name": "Quality / Approval Rate",
                "value": f"{pass_rate:.1f}%",
                "formula": "Passed / Total Audited",
                "source": f"`{status_col}`",
                "confidence": conf,
                "warnings": "CRITICAL: Compliance rate below 95% threshold" if pass_rate < 95.0 else "None"
            })

    return kpis
