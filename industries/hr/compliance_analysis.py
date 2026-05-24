"""
Compliance, policy adherence, and risk metrics.
GOVERNANCE: CRITICAL - Operational compliance ONLY.
Report incidents, not individuals.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_compliance_metrics(df):
    """Calculates compliance and regulatory adherence KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Compliance metrics
    employee_col = first_column(df, ["employee_id", "emp_id", "staff_id"])
    policy_col = first_column(df, ["policy_name", "policy_id", "training_type"])
    completed_col = first_column(df, ["completed", "acknowledgment_flag", "completion_flag"])
    incident_col = first_column(df, ["incident_count", "incidents", "violation_count"])
    harassment_col = first_column(df, ["harassment_case", "harass_incident", "complaint"])
    safety_col = first_column(df, ["safety_training_completed", "safety_cert", "safety_flag"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, policy_col, completed_col, incident_col, harassment_col, safety_col] if col])
    
    # Total employees
    total_employees = df[employee_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Compliance",
        name="Total Employees",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Policy compliance
    if completed_col:
        completed_mask = df[completed_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'completed'])
        completed_count = completed_mask.sum()
        completion_rate = (completed_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="✅ Compliance",
            name="Policy Completion Count",
            value=f"{completed_count:,}",
            formula="Count(Completed = True)",
            source=f"`{completed_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="✅ Compliance",
            name="Policy Completion Rate",
            value=f"{completion_rate:.2f}%",
            formula="(Completed / Total) * 100",
            source=f"`{completed_col}`",
            confidence=conf,
            warnings="Low compliance (<95%)" if completion_rate < 95 else warns
        ))
    
    # Incident reporting (OPERATIONAL - not individual profiling)
    if incident_col and pd.api.types.is_numeric_dtype(df[incident_col]):
        total_incidents = df[incident_col].sum()
        incident_rate = (total_incidents / total_employees * 100) if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Total Reported Incidents",
            value=f"{total_incidents:,}",
            formula="Sum(Incident Count)",
            source=f"`{incident_col}`",
            confidence=conf,
            warnings="Elevated incident rate" if incident_rate > 5 else warns
        ))
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Incident Rate",
            value=f"{incident_rate:.2f}%",
            formula="(Total Incidents / Total Employees) * 100",
            source=f"`{incident_col}`",
            confidence=conf,
            warnings="Critical incident rate (>10%)" if incident_rate > 10 else warns
        ))
    
    # Harassment/misconduct incidents (OPERATIONAL REPORTING ONLY)
    if harassment_col:
        harassment_mask = df[harassment_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'case'])
        harassment_count = harassment_mask.sum()
        harassment_rate = (harassment_count / total_employees * 100) if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Reported Misconduct Cases",
            value=f"{harassment_count:,}",
            formula="Count(Reported Cases)",
            source=f"`{harassment_col}`",
            confidence=conf,
            warnings="⚠️ Review investigation status" if harassment_count > 0 else warns
        ))
        
        kpis.append(safe_kpi(
            category="⚠️ Risk",
            name="Case Report Rate",
            value=f"{harassment_rate:.2f}%",
            formula="(Cases / Total Employees) * 100",
            source=f"`{harassment_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Safety training
    if safety_col:
        safety_mask = df[safety_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'completed'])
        safety_count = safety_mask.sum()
        safety_rate = (safety_count / total_employees * 100) if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="🛡️ Safety",
            name="Safety Training Completed",
            value=f"{safety_count:,} ({safety_rate:.1f}%)",
            formula="Count(Safety Training = Complete)",
            source=f"`{safety_col}`",
            confidence=conf,
            warnings="Low safety certification (<95%)" if safety_rate < 95 else warns
        ))
    
    # Total policies tracked
    if policy_col:
        unique_policies = df[policy_col].nunique()
        
        kpis.append(safe_kpi(
            category="✅ Compliance",
            name="Policies Tracked",
            value=f"{unique_policies}",
            formula="Count(Distinct Policies)",
            source=f"`{policy_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
