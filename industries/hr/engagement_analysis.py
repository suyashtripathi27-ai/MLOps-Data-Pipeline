import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_engagement_metrics(df):
    kpis = []
    if len(df) == 0:
        return kpis
    
    # Aliases
    job_sat_col = first_column(df, ["jobsatisfaction", "job_satisfaction", "satisfaction_score"])
    env_sat_col = first_column(df, ["environmentsatisfaction", "environment_satisfaction"])
    rel_sat_col = first_column(df, ["relationshipsatisfaction", "relationship_satisfaction"])
    wlb_col = first_column(df, ["worklifebalance", "work_life_balance"])
    
    # 🛑 Notice: We completely removed the `if not employee_col` kill-switch!
    
    # Total employees assessed is just the number of rows
    total_employees = len(df)
    kpis.append(safe_kpi(
        category="👥 Engagement", name="Total Employees Assessed",
        value=f"{total_employees:,}", formula="Total Rows",
        source="System", confidence=0.99, warnings="None"
    ))
    
    conf, warns = confidence_for(df, [col for col in [job_sat_col, env_sat_col, rel_sat_col, wlb_col] if col])
    
    if job_sat_col and pd.api.types.is_numeric_dtype(df[job_sat_col]):
        avg_job_sat = df[job_sat_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📊 Engagement Metrics", name="Avg Job Satisfaction (Out of 4)",
            value=f"{avg_job_sat:.2f}", formula="Mean(JobSatisfaction)",
            source=f"`{job_sat_col}`", confidence=conf,
            warnings="Low job satisfaction" if avg_job_sat < 2.5 else warns
        ))

    if env_sat_col and pd.api.types.is_numeric_dtype(df[env_sat_col]):
        avg_env_sat = df[env_sat_col].dropna().mean()
        kpis.append(safe_kpi(
            category="📊 Engagement Metrics", name="Avg Environment Satisfaction (Out of 4)",
            value=f"{avg_env_sat:.2f}", formula="Mean(EnvironmentSatisfaction)",
            source=f"`{env_sat_col}`", confidence=conf,
            warnings="Low environment satisfaction" if avg_env_sat < 2.5 else warns
        ))

    if wlb_col and pd.api.types.is_numeric_dtype(df[wlb_col]):
        avg_wlb = df[wlb_col].dropna().mean()
        kpis.append(safe_kpi(
            category="⚖️ Work-Life Balance", name="Avg Work-Life Balance (Out of 4)",
            value=f"{avg_wlb:.2f}", formula="Mean(WorkLifeBalance)",
            source=f"`{wlb_col}`", confidence=conf,
            warnings="Burnout risk detected" if avg_wlb < 2.5 else warns
        ))
        
    return kpis
