"""
Compliance, AML/KYC, and regulatory risk KPIs.
"""
import pandas as pd
from utils.kpi_helpers import (
    first_column, safe_kpi, excluded_kpi, confidence_for, safe_exists, safe_numeric, safe_numeric_series
)

def calc_compliance_metrics(df):
    kpis = []
    missing_capabilities = []
    
    if len(df) == 0: return kpis

    aml_flag_col = first_column(df, ["aml_flag", "aml_alert", "suspicious_flag"])
    kyc_col = first_column(df, ["kyc_status", "kyc_verified", "verification_status"])
    large_txn_col = first_column(df, ["is_large_transaction", "high_value", "ctc_flag"])
    amount_col = first_column(df, ["amount", "transaction_amount"])

    conf, warns = confidence_for(df, [aml_flag_col, kyc_col, large_txn_col])

    if safe_exists(df, aml_flag_col):
        aml_series = df[aml_flag_col].astype(str).str.lower().isin(["true", "1", "yes", "flagged"])
        aml_count = aml_series.sum()
        aml_rate = (aml_count / len(df) * 100) if len(df) > 0 else 0
        kpis.append(safe_kpi(
            category="🛡️ Compliance Analysis", name="AML Flagged Transactions",
            value=f"{int(aml_count)} ({aml_rate:.2f}%)", formula="Count(AML Flag) / Total",
            source=f"`{aml_flag_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("AML Analytics unavailable: Missing flag column.")

    if safe_exists(df, kyc_col):
        kyc_verified = (df[kyc_col].astype(str).str.lower().isin(["verified", "passed", "complete"])).sum()
        kyc_rate = (kyc_verified / len(df) * 100) if len(df) > 0 else 0
        kpis.append(safe_kpi(
            category="🛡️ Compliance Analysis", name="KYC Verification Rate",
            value=f"{kyc_rate:.2f}%", formula="Verified / Total * 100",
            source=f"`{kyc_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("KYC Analytics unavailable: Missing status column.")

    if safe_exists(df, large_txn_col) and safe_numeric(df, amount_col):
        large_series = df[large_txn_col].astype(str).str.lower().isin(["true", "1", "yes"])
        large_count = large_series.sum()
        clean_amount = safe_numeric_series(df, amount_col)
        large_volume = clean_amount[large_series].sum()
        
        kpis.append(safe_kpi(
            category="🛡️ Compliance Analysis", name="Large Transactions (>10K)",
            value=f"{int(large_count)} (${large_volume:,.2f})", formula="Count & Sum Large Txns",
            source=f"`{large_txn_col}`, `{amount_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("Large Transaction Analysis unavailable: Requires 'flag' and numeric 'amount'.")

    for missing in missing_capabilities:
        kpis.append(excluded_kpi(category="⚠️ System Audit", name="Data Gap Detected", source="Diagnostic", reason=missing))

    return kpis
