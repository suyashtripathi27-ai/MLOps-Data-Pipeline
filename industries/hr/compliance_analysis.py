"""
Compliance, policy adherence, and risk metrics.
GOVERNANCE: CRITICAL - Operational compliance ONLY.
Report incidents, not individuals.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# HR Industry Configuration
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_compliance_metrics(df, enable_debug=False):
    """Calculates compliance and regulatory adherence KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Compliance metrics
    employee_col, employee_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    policy_col, policy_series = engine.get_column(["policy_name", "policy_id", "training_type"])
    completed_col, completed_series = engine.get_column(["completed", "acknowledgment_flag", "completion_flag"])
    incident_col, incident_series = engine.get_numeric(["incident_count", "incidents", "violation_count"])
    harassment_col, harassment_series = engine.get_column(["harassment_case", "harass_incident", "complaint"])
    safety_col, safety_series = engine.get_column(["safety_training_completed", "safety_cert", "safety_flag"])
    
    if not employee_col:
        return kpis
    
    # Total employees
    total_employees = employee_series.nunique()
    
    kpis.append(engine.build_kpi(
        category="👥 Compliance",
        name="Total Employees",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`"
    ))
    
    # Policy compliance
    if completed_col and not completed_series.empty:
        completed_mask = completed_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'completed'])
        completed_count = completed_mask.sum()
        completion_rate = (completed_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="✅ Compliance",
            name="Policy Completion Count",
            value=f"{completed_count:,}",
            formula="Count(Completed = True)",
            source=f"`{completed_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="✅ Compliance",
            name="Policy Completion Rate",
            value=f"{completion_rate:.2f}%",
            formula="(Completed / Total) * 100",
            source=f"`{completed_col}`",
            warnings="Low compliance (<95%)" if completion_rate < 95 else None
        ))
    
    # Incident reporting (OPERATIONAL - not individual profiling)
    if incident_col and not incident_series.empty:
        total_incidents = incident_series.sum()
        incident_rate = (total_incidents / total_employees * 100) if total_employees > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk",
            name="Total Reported Incidents",
            value=f"{total_incidents:,}",
            formula="Sum(Incident Count)",
            source=f"`{incident_col}`",
            warnings="Elevated incident rate (>5%)" if incident_rate > 5 else None
        ))
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk",
            name="Incident Rate",
            value=f"{incident_rate:.2f}%",
            formula="(Total Incidents / Total Employees) * 100",
            source=f"`{incident_col}`"
        ))
    
    # Harassment cases (aggregated, operational only)
    if harassment_col and not harassment_series.empty:
        harassment_mask = harassment_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'reported', 'case'])
        harassment_count = harassment_mask.sum()
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk",
            name="Harassment Cases Reported",
            value=f"{harassment_count}",
            formula="Count(Harassment = True)",
            source=f"`{harassment_col}`",
            warnings="Harassment incidents detected" if harassment_count > 0 else None,
            sensitivity="HR_SENSITIVE"
        ))
    
    # Safety training
    if safety_col and not safety_series.empty:
        safety_mask = safety_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'completed', 'certified'])
        safety_count = safety_mask.sum()
        safety_rate = (safety_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🛡️ Safety",
            name="Safety Training Completion",
            value=f"{safety_count:,} ({safety_rate:.1f}%)",
            formula="Count(Safety Training = Completed)",
            source=f"`{safety_col}`",
            warnings="Low safety training (<95%)" if safety_rate < 95 else None
        ))
    
    return kpis
