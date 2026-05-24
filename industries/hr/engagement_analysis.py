"""
Employee engagement and satisfaction metrics.
GOVERNANCE: CRITICAL - Measure OPERATIONAL engagement signals ONLY.
DO NOT infer emotions, mental health, personality, or intent.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_engagement_metrics(df):
    """Calculates engagement and satisfaction KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Combined Universal Aliases
    employee_col = first_column(df, ["employeenumber", "employee_id", "emp_id", "staff_id"])
    job_sat_col = first_column(df, ["jobsatisfaction", "job_satisfaction", "satisfaction_score", "satisfaction_rating"])
    env_sat_col = first_column(df, ["environmentsatisfaction", "environment_satisfaction"])
    rel_sat_col = first_column(df, ["relationshipsatisfaction", "relationship_satisfaction"])
    wlb_col = first_column(df, ["worklifebalance", "work_life_balance"])
    
    # Advanced / Future metrics
    engagement_col = first_column(df, ["engagement_score", "engagement_rating", "engagement_level"])
    eNPS_col = first_column(df, ["eNPS", "employee_nps", "nps_score"])
    survey_col = first_column(df, ["pulse_score", "survey_response", "feedback_score"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, job_sat_col, env_sat_col, rel_sat_col, wlb_col] if col])
    
    total_employees = df[employee_col].nunique()
    kpis.append(safe_kpi(
        category="👥 Engagement", name="Total Employees Assessed",
        value=f"{total_employees:,}", formula="Count(Distinct Employees)",
        source=f"`{employee_col}`", confidence=conf, warnings=warns
    ))
    
    if job_sat_col and pd.api.types.is_numeric_dtype(df[job_sat_col]):
        avg_job_sat = df[job_sat_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📊 Engagement Metrics", name="Avg Job Satisfaction",
            value=f"{avg_job_sat:.2f}", formula="Mean(JobSatisfaction)",
            source=f"`{job_sat_col}`", confidence=conf,
            warnings="Low job satisfaction" if avg_job_sat < 2.5 else warns
        ))

    if env_sat_col and pd.api.types.is_numeric_dtype(df[env_sat_col]):
        avg_env_sat = df[env_sat_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📊 Engagement Metrics", name="Avg Environment Satisfaction",
            value=f"{avg_env_sat:.2f}", formula="Mean(EnvironmentSatisfaction)",
            source=f"`{env_sat_col}`", confidence=conf,
            warnings="Low environment satisfaction" if avg_env_sat < 2.5 else warns
        ))

    if rel_sat_col and pd.api.types.is_numeric_dtype(df[rel_sat_col]):
        avg_rel_sat = df[rel_sat_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📊 Engagement Metrics", name="Avg Relationship Satisfaction",
            value=f"{avg_rel_sat:.2f}", formula="Mean(RelationshipSatisfaction)",
            source=f"`{rel_sat_col}`", confidence=conf, warnings=warns
        ))

    if wlb_col and pd.api.types.is_numeric_dtype(df[wlb_col]):
        avg_wlb = df[wlb_col].dropna().mean()
        kpis.append(safe_kpi(
            category="⚖️ Work-Life Balance", name="Avg Work-Life Balance",
            value=f"{avg_wlb:.2f}", formula="Mean(WorkLifeBalance)",
            source=f"`{wlb_col}`", confidence=conf,
            warnings="Burnout risk detected" if avg_wlb < 2.5 else warns
        ))

    # The future-proof math (will safely skip if these columns don't exist yet)
    if eNPS_col and pd.api.types.is_numeric_dtype(df[eNPS_col]):
        avg_nps = df[eNPS_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📊 Engagement Metrics", name="Avg eNPS",
            value=f"{avg_nps:.2f}", formula="Mean(eNPS Score)",
            source=f"`{eNPS_col}`", confidence=conf,
            warnings="Low eNPS (<30)" if avg_nps < 30 else warns
        ))
        
    return kpis
