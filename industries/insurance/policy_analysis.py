"""
Policy portfolio KPIs: retention, lapse, premium growth.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

INSURANCE_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 25,
}


def calc_policy_metrics(df, enable_debug=False):
    """
    Policy Retention Rate = Policies Renewed / Policies Eligible for Renewal
    Premium Growth Rate = (Current Period Premium - Prior Period Premium) / Prior Period Premium
    """
    engine = KPIEngine(df, industry_config=INSURANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()

    kpis = []
    if len(df) == 0:
        return kpis

    status_col, status_series = engine.get_column(["policy_status_ins", "policy_state", "policy_disposition"])
    policy_type_col, policy_type_series = engine.get_column(["policy_type", "product_type", "coverage_type"])
    premium_col, premium_series = engine.get_numeric(["premium_amount", "annual_premium", "premium_paid"])

    num_policies = len(df)

    if status_col is not None:
        lower_status = status_series.astype(str).str.lower()
        lapsed_terms = ["lapsed", "cancelled", "non-renewed", "non_renewed", "expired"]
        lapsed_count = lower_status.isin(lapsed_terms).sum()
        lapse_rate = (lapsed_count / num_policies * 100) if num_policies > 0 else 0
        retention_rate = 100 - lapse_rate
        kpis.append(engine.build_kpi(
            category="📑 Policy Portfolio", name="Policy Lapse Rate",
            value=f"{lapse_rate:.2f}%", formula="Lapsed/Cancelled Policies / Total Policies * 100",
            source=f"`{status_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="📑 Policy Portfolio", name="Policy Retention Rate",
            value=f"{retention_rate:.2f}%", formula="100% - Lapse Rate",
            source=f"`{status_col}`"
        ))
    else:
        kpis.append(engine.log_missing("📑 Policy Portfolio", "Retention Rate", "Missing 'policy_status' column."))

    if policy_type_col is not None:
        top_type = policy_type_series.value_counts()
        if not top_type.empty:
            top_type_share = (top_type.iloc[0] / num_policies * 100) if num_policies > 0 else 0
            kpis.append(engine.build_kpi(
                category="📑 Policy Portfolio", name="Top Policy Type Concentration",
                value=f"{top_type.index[0]} ({top_type_share:.1f}%)",
                formula="Most Common Policy Type / Total Policies * 100",
                source=f"`{policy_type_col}`"
            ))
    else:
        kpis.append(engine.log_missing("📑 Policy Portfolio", "Policy Type Concentration", "Missing 'policy_type' column."))

    if premium_col is not None:
        kpis.append(engine.build_kpi(
            category="📑 Policy Portfolio", name="Avg Premium per Policy",
            value=f"${premium_series.mean():,.2f}", formula="Mean(Premium Amount)",
            source=f"`{premium_col}`"
        ))

    if enable_debug:
        engine.print_execution_log()

    return kpis
