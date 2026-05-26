"""
Compliance, policy adherence, and risk metrics.
GOVERNANCE: CRITICAL - Operational compliance ONLY.
Report incidents, not individuals.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_compliance_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    emp_col, emp_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    pol_col, pol_series = engine.get_column(["policy_name", "policy_id", "training_type"])
    comp_col, comp_series = engine.get_column(["completed", "acknowledgment_flag", "completion_flag"])
    inc_col, inc_series = engine.get_numeric(["incident_count", "incidents", "violation_count"])
    har_col, har_series = engine.get_column(["harassment_case", "harass_incident", "complaint"])
    saf_col, saf_series = engine.get_column(["safety_training_completed", "safety_cert", "safety_flag"])
    
    if emp_col is not None:
        total_employees = emp_series.nunique()
        kpis.append(engine.build_kpi(
            category="👥 Compliance", name="Total Employees",
            value=f"{total_employees:,}", formula="Count(Distinct Employees)", source=f"`{emp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Compliance", "Total Employees", "Missing employee ID."))
        return kpis 
    
    if comp_col is not None:
        comp_mask = comp_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'completed'])
        comp_count = comp_mask.sum()
        comp_rate = (comp_count / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="✅ Compliance", name="Policy Completion Count",
            value=f"{comp_count:,}", formula="Count(Completed = True)", source=f"`{comp_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="✅ Compliance", name="Policy Completion Rate",
            value=f"{comp_rate:.2f}%", formula="(Completed / Total) * 100", 
            source=f"`{comp_col}`", warnings="Low compliance (<95%)" if comp_rate < 95 else "None"
        ))
    else:
        kpis.append(engine.log_missing("✅ Compliance", "Policy Adherence", "Missing completion flag."))
    
    if inc_col is not None:
        total_inc = inc_series.sum()
        inc_rate = (total_inc / total_employees * 100) if total_employees > 0 else 0
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Total Reported Incidents",
            value=f"{total_inc:,}", formula="Sum(Incident Count)", 
            source=f"`{inc_col}`", warnings="Elevated incident rate (>5%)" if inc_rate > 5 else "None"
        ))
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Incident Rate",
            value=f"{inc_rate:.2f}%", formula="(Incidents / Employees) * 100", source=f"`{inc_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⚠️ Risk", "Incident Reporting", "Missing incident count data."))
    
    if har_col is not None:
        har_mask = har_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'reported', 'case'])
        har_count = har_mask.sum()
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Harassment Cases Reported",
            value=f"{har_count}", formula="Count(Harassment = True)", 
            source=f"`{har_col}`", warnings="Harassment incidents detected" if har_count > 0 else "None", sensitivity="HR_SENSITIVE"
        ))
    else:
        kpis.append(engine.log_missing("⚠️ Risk", "Harassment Cases", "Missing harassment tracking data."))
    
    if saf_col is not None:
        saf_mask = saf_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'completed', 'certified'])
        saf_count = saf_mask.sum()
        saf_rate = (saf_count / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="🛡️ Safety", name="Safety Training Completion",
            value=f"{saf_count:,} ({saf_rate:.1f}%)", formula="Count(Safety = Completed)", 
            source=f"`{saf_col}`", warnings="Low safety training (<95%)" if saf_rate < 95 else "None"
        ))
    else:
        kpis.append(engine.log_missing("🛡️ Safety", "Safety Training", "Missing safety training flag."))
    
    return kpis
