"""Fraud detection KPIs: counts and rates of flagged transactions."""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_fraud_metrics(df):
    kpis = []
    fraud_flag = first_column(df, ["fraud_flag", "is_fraud", "suspicious"]) 
    amount_col = first_column(df, ["amount", "transaction_amount", "value"]) 

    if not fraud_flag:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [fraud_flag, amount_col])
    fraud_count = int(df[fraud_flag].astype(bool).sum())
    total = len(df)
    fraud_rate = fraud_count / total if total > 0 else 0

    kpis.append({
        "category": "🚨 Fraud",
        "name": "Suspicious Transaction Count",
        "value": f"{fraud_count}",
        "formula": "Count(Flagged Transactions)",
        "source": f"`{fraud_flag}`",
        "confidence": conf,
        "warnings": warns,
    })

    kpis.append({
        "category": "🚨 Fraud",
        "name": "Suspicious Transaction Rate",
        "value": f"{fraud_rate:.2%}",
        "formula": "Flagged / Total",
        "source": f"`{fraud_flag}`",
        "confidence": conf,
        "warnings": warns,
    })

    if amount_col:
        fraud_volume = df[df[fraud_flag].astype(bool)][amount_col].sum()
        kpis.append({
            "category": "🚨 Fraud",
            "name": "Suspicious Transaction Volume",
            "value": f"${fraud_volume:,.2f}",
            "formula": "Sum(Amount where Fraud Flag)",
            "source": f"`{fraud_flag}`, `{amount_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
