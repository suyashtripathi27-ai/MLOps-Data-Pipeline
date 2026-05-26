"""
Compliance, AML/KYC, and regulatory risk KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

BANKING_CONFIG = {
    "missing_data_threshold": 5,        
    "score_deduction_for_warning": 20,  
    "low_confidence_threshold": 25,     
}

def calc_compliance_metrics(df, enable_debug=False):
    """
    Calculate compliance KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    
    engine = KPIEngine(df, industry_config=BANKING_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0: 
        return kpis

    aml_col, aml_series = engine.get_column(["aml_flag", "aml_alert", "suspicious_flag"])
    kyc_col, kyc_series = engine.get_column(["kyc_status", "kyc_verified", "verification_status"])
    txn_col, txn_series = engine.get_column(["is_large_transaction", "high_value", "ctc_flag"])
    amt_col, amt_series = engine.get_numeric(["amount", "transaction_amount"])

    if aml_col is not None:
        aml_flags = aml_series.astype(str).str.lower().isin(["true", "1", "yes", "flagged"])
        aml_count = aml_flags.sum()
        aml_rate = (aml_count / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="🛡️ Compliance Analysis", name="AML Flagged Transactions",
            value=f"{int(aml_count)} ({aml_rate:.2f}%)", formula="Count(AML Flag) / Total", source=f"`{aml_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🛡️ Compliance Analysis", "AML Flags", "Missing AML flag column."))

    if kyc_col is not None:
        kyc_verified = kyc_series.astype(str).str.lower().isin(["verified", "passed", "complete"]).sum()
        kyc_rate = (kyc_verified / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="🛡️ Compliance Analysis", name="KYC Verification Rate",
            value=f"{kyc_rate:.2f}%", formula="Verified / Total * 100", source=f"`{kyc_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🛡️ Compliance Analysis", "KYC Verification", "Missing KYC status column."))

    if txn_col is not None and amt_col is not None:
        df_temp = pd.concat([txn_series, amt_series], axis=1).dropna()
        large_flags = df_temp[txn_col].astype(str).str.lower().isin(["true", "1", "yes"])
        large_count = large_flags.sum()
        large_volume = df_temp.loc[large_flags, amt_col].sum()
        
        kpis.append(engine.build_kpi(
            category="🛡️ Compliance Analysis", name="Large Transactions (>10K)",
            value=f"{int(large_count)} (${large_volume:,.2f})", formula="Count & Sum Large Txns", source=f"`{txn_col}`, `{amt_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🛡️ Compliance Analysis", "Large Transactions", "Requires transaction flag and numeric amount."))

    if enable_debug:
        engine.print_execution_log()
    
    return kpis
