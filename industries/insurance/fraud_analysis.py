"""
Fraud exposure KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

INSURANCE_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 25,
}


def calc_fraud_metrics(df, enable_debug=False):
    """
    Fraud Exposure Rate = Flagged/Suspicious Claims / Total Claims
    """
    engine = KPIEngine(df, industry_config=INSURANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()

    kpis = []
    if len(df) == 0:
        return kpis

    fraud_col, fraud_series = engine.get_column(["fraud_flag_ins", "is_fraud", "fraud_indicator", "suspicious_claim"])
    claim_amt_col, claim_amt_series = engine.get_numeric(["claim_amount", "claim_paid", "claimed_amount"])

    if fraud_col is not None:
        num_claims = len(df)
        lower_flag = fraud_series.astype(str).str.lower()
        fraud_terms = ["true", "yes", "1", "flagged", "suspicious"]
        fraud_count = lower_flag.isin(fraud_terms).sum()
        fraud_rate = (fraud_count / num_claims * 100) if num_claims > 0 else 0
        kpis.append(engine.build_kpi(
            category="🚨 Fraud Risk", name="Fraud Exposure Rate",
            value=f"{fraud_rate:.2f}%", formula="Flagged Claims / Total Claims * 100",
            source=f"`{fraud_col}`"
        ))

        if claim_amt_col is not None and fraud_count > 0:
            flagged_mask = lower_flag.isin(fraud_terms)
            fraud_value = claim_amt_series[flagged_mask].fillna(0).sum()
            kpis.append(engine.build_kpi(
                category="🚨 Fraud Risk", name="Total Value of Flagged Claims",
                value=f"${fraud_value:,.2f}", formula="Sum(Claim Amount WHERE Fraud Flagged)",
                source=f"`{claim_amt_col}`, `{fraud_col}`"
            ))
    else:
        kpis.append(engine.log_missing("🚨 Fraud Risk", "Fraud Exposure Rate", "Missing 'fraud_flag' column."))

    if enable_debug:
        engine.print_execution_log()

    return kpis
