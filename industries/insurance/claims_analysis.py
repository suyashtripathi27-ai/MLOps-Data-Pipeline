"""
Claims management KPIs: frequency, severity, settlement behavior.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

INSURANCE_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 25,
}


def calc_claims_metrics(df, enable_debug=False):
    """
    Claims Frequency = Number of Claims / Number of Policies (exposure units)
    Claims Severity = Total Claims Paid / Number of Claims
    """
    engine = KPIEngine(df, industry_config=INSURANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()

    kpis = []
    if len(df) == 0:
        return kpis

    claim_amt_col, claim_amt_series = engine.get_numeric(["claim_amount", "claim_paid", "claimed_amount", "payout_amount"])
    policy_col, policy_series = engine.get_column(["policy_number", "policy_no", "policy_id"])
    claim_status_col, claim_status_series = engine.get_column(["claim_status", "claim_state", "claim_outcome"])

    num_claims = len(df)

    if claim_amt_col is not None:
        total_claims_paid = claim_amt_series.fillna(0).sum()
        avg_severity = claim_amt_series.mean()
        kpis.append(engine.build_kpi(
            category="🧾 Claims Management", name="Total Claims Paid",
            value=f"${total_claims_paid:,.2f}", formula="Sum(Claim Amount)", source=f"`{claim_amt_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="🧾 Claims Management", name="Claims Severity (Avg Cost per Claim)",
            value=f"${avg_severity:,.2f}", formula="Total Claims Paid / Number of Claims",
            source=f"`{claim_amt_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🧾 Claims Management", "Claims Severity", "Missing numeric 'claim_amount' column."))

    if policy_col is not None:
        num_policies = policy_series.nunique()
        claims_frequency = (num_claims / num_policies) if num_policies > 0 else 0
        kpis.append(engine.build_kpi(
            category="🧾 Claims Management", name="Claims Frequency",
            value=f"{claims_frequency:.3f}", formula="Number of Claims / Number of Distinct Policies",
            source=f"`{policy_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🧾 Claims Management", "Claims Frequency", "Missing 'policy_number' column."))

    if claim_status_col is not None:
        lower_status = claim_status_series.astype(str).str.lower()
        open_terms = ["open", "pending", "in review", "in_review"]
        open_count = lower_status.isin(open_terms).sum()
        open_rate = (open_count / num_claims * 100) if num_claims > 0 else 0
        kpis.append(engine.build_kpi(
            category="🧾 Claims Management", name="Open/Pending Claims Rate",
            value=f"{open_rate:.2f}%", formula="Open Claims / Total Claims * 100",
            source=f"`{claim_status_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🧾 Claims Management", "Open Claims Rate", "Missing 'claim_status' column."))

    if enable_debug:
        engine.print_execution_log()

    return kpis
