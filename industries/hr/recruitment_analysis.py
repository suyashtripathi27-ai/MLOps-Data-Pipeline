"""
Recruitment efficiency, hiring pipeline, and talent acquisition metrics.
GOVERNANCE: Process metrics ONLY - No candidate personality assessment.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_recruitment_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    cand_col, cand_series = engine.get_column(["candidate_id", "applicant_id", "hire_id"])
    pos_col, pos_series = engine.get_column(["position_id", "job_id", "requisition_id"])
    hired_col, hired_series = engine.get_column(["hired", "offer_accepted", "hired_flag"])
    tth_col, tth_series = engine.get_numeric(["time_to_hire_days", "days_to_hire", "hiring_duration"])
    cost_col, cost_series = engine.get_numeric(["recruitment_cost", "cost_per_hire", "hiring_cost"])
    
    if cand_col is not None:
        kpis.append(engine.build_kpi(
            category="👥 Recruitment", name="Total Candidates",
            value=f"{cand_series.nunique():,}", formula="Count(Distinct Candidates)", source=f"`{cand_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Recruitment", "Total Candidates", "Missing candidate ID."))
        return kpis # Hard stop if no candidates

    if pos_col is not None:
        kpis.append(engine.build_kpi(
            category="📋 Positions", name="Total Open Positions",
            value=f"{pos_series.nunique()}", formula="Count(Distinct Positions)", source=f"`{pos_col}`"
        ))
    else:
        kpis.append(engine.log_missing("📋 Positions", "Open Positions", "Missing position IDs."))

    hired_count = 0
    if hired_col is not None:
        hired_mask = hired_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'hired', 'accepted'])
        hired_count = hired_mask.sum()
        hiring_rate = (hired_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="✅ Hires", name="Total Hired",
            value=f"{hired_count:,}", formula="Count(Hired = True)", source=f"`{hired_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="✅ Hires", name="Hiring Conversion Rate",
            value=f"{hiring_rate:.2f}%", formula="(Hired / Total Candidates) * 100", 
            source=f"`{hired_col}`", warnings="Low conversion rate (<5%)" if hiring_rate < 5 else "None"
        ))
    else:
        kpis.append(engine.log_missing("✅ Hires", "Hiring Conversion", "Missing hired flag."))

    # 🛑 THE FACADE FIX IS HERE
    if tth_col is not None and not tth_series.empty:
        is_valid, reason = engine.validate_business_rule("duration", tth_series)
        if is_valid:
            valid_tth = tth_series.dropna()
            kpis.append(engine.build_kpi(
                category="⏱️ Hiring Timeline", name="Avg Time-to-Hire",
                value=f"{valid_tth.mean():.0f} days", formula="Mean(Days to Hire)", 
                source=f"`{tth_col}`", warnings="Long hiring process (>60 days)" if valid_tth.mean() > 60 else "None"
            ))
        else:
            kpis.append(engine.log_missing("⏱️ Hiring Timeline", "Time-to-Hire", f"Data corrupted: {reason}"))
    else:
        kpis.append(engine.log_missing("⏱️ Hiring Timeline", "Time-to-Hire", "Missing duration data."))

    if cost_col is not None:
        total_cost = cost_series.sum()
        kpis.append(engine.build_kpi(
            category="💰 Recruitment Cost", name="Total Recruitment Cost",
            value=f"${total_cost:,.2f}", formula="Sum(Cost)", source=f"`{cost_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💰 Recruitment Cost", "Recruitment Cost", "Missing cost data."))

    return kpis
