"""
Compliance, AML/KYC, and regulatory risk KPIs.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from .reliability import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_compliance_metrics(df):
    """Calculates compliance and regulatory risk KPIs."""
    kpis = []
    aml_flag_col = _first_column(df, ["aml_flag", "aml_alert", "suspicious_flag"])
    kyc_col = _first_column(df, ["kyc_status", "kyc_verified", "verification_status"])
    large_txn_col = _first_column(df, ["is_large_transaction", "high_value", "ctc_flag"])
    amount_col = _first_column(df, ["amount", "transaction_amount"])

    if len(df) == 0:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [col for col in [aml_flag_col, kyc_col, large_txn_col] if col])

    if aml_flag_col:
        aml_series = df[aml_flag_col].astype(str).str.lower().isin(["true", "1", "yes", "flagged"])
        aml_count = aml_series.sum()
        aml_rate = (aml_count / len(df) * 100) if len(df) > 0 else 0
        kpis.append({
            "category": "🛡️ Compliance Analysis",
            "name": "AML Flagged Transactions",
            "value": f"{int(aml_count)} ({aml_rate:.2f}%)",
            "formula": "Count(AML Flag = True) / Total * 100",
            "source": f"`{aml_flag_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if kyc_col:
        kyc_verified = (df[kyc_col].astype(str).str.lower().isin(["verified", "passed", "complete"])).sum()
        kyc_rate = (kyc_verified / len(df) * 100) if len(df) > 0 else 0
        kpis.append({
            "category": "🛡️ Compliance Analysis",
            "name": "KYC Verification Rate",
            "value": f"{kyc_rate:.2f}%",
            "formula": "Verified Customers / Total Customers * 100",
            "source": f"`{kyc_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if large_txn_col and amount_col:
        large_series = df[large_txn_col].astype(str).str.lower().isin(["true", "1", "yes"])
        large_count = large_series.sum()
        large_volume = df.loc[large_series, amount_col].sum()
        kpis.append({
            "category": "🛡️ Compliance Analysis",
            "name": "Large Transactions (>10K)",
            "value": f"{int(large_count)} (${large_volume:,.2f})",
            "formula": "Count(Amount > 10000) & Sum",
            "source": f"`{large_txn_col}`, `{amount_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
