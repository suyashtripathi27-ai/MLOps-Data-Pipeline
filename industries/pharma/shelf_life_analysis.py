import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def calc_shelf_life_metrics(df):
    """
    Analyzes expiration risk and remaining inventory shelf life.
    """
    kpis = []
    # Look for common shelf-life or expiry-related columns
    expiry_col = next((c for c in df.columns if 'expiry' in c.lower() or 'exp' in c.lower()), None)
    
    if not expiry_col:
        return kpis

    # Ensure the column is datetime-ready
    df[expiry_col] = pd.to_datetime(df[expiry_col], errors='coerce')
    
    # Calculate Confidence
    conf, warns = evaluate_kpi_confidence(df, [expiry_col])

    # 1. Near-Expiry Risk (Items expiring in < 90 days)
    today = pd.Timestamp.now()
    ninety_days = today + pd.Timedelta(days=90)
    near_expiry = (df[expiry_col] <= ninety_days) & (df[expiry_col] >= today)
    near_expiry_count = near_expiry.sum()

    kpis.append({
        "category": "🧪 Quality & Compliance",
        "name": "Near-Expiry Batches (<90 Days)",
        "value": f"{near_expiry_count} batches",
        "formula": "COUNT(ExpiryDate - Today < 90 Days)",
        "source": f"`{expiry_col}`",
        "confidence": conf,
        "warnings": "High expiry risk — expedite distribution" if near_expiry_count > 10 else warns
    })

    # 2. Expired Batch Count
    expired = (df[expiry_col] < today).sum()
    kpis.append({
        "category": "🧪 Quality & Compliance",
        "name": "Expired Batches",
        "value": f"{expired} batches",
        "formula": "COUNT(ExpiryDate < Today)",
        "source": f"`{expiry_col}`",
        "confidence": conf,
        "warnings": "⚠️ CRITICAL: Remove expired batches immediately" if expired > 0 else "None"
    })

    return kpis
