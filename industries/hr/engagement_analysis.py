"""
Employee engagement, satisfaction, and morale metrics.
GOVERNANCE: Operational aggregated metrics ONLY - No individual psychoanalysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# HR Industry Configuration
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_engagement_metrics(df, enable_debug=False):
    """Calculates engagement and satisfaction KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Engagement metrics
    job_sat_col, job_sat_series = engine.get_numeric(["JobSatisfaction", "jobsatisfaction", "job_satisfaction", "satisfaction_score"])
    env_sat_col, env_sat_series = engine.get_numeric(["EnvironmentSatisfaction", "environmentsatisfaction", "environment_satisfaction"])
    rel_sat_col, rel_sat_series = engine.get_numeric(["RelationshipSatisfaction", "relationshipsatisfaction", "relationship_satisfaction"])
    wlb_col, wlb_series = engine.get_numeric(["WorkLifeBalance", "worklifebalance", "work_life_balance"])
    
    # Total employees assessed
    total_employees = len(df)
    kpis.append(engine.build_kpi(
        category="👥 Engagement",
        name="Total Employees Assessed",
        value=f"{total_employees:,}",
        formula="Total Rows",
        source="System"
    ))
    
    # Job satisfaction
    if job_sat_col and not job_sat_series.empty:
        avg_job_sat = job_sat_series.dropna().mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics",
            name="Avg Job Satisfaction (Out of 4)",
            value=f"{avg_job_sat:.2f}",
            formula="Mean(JobSatisfaction)",
            source=f"`{job_sat_col}`",
            warnings="Low job satisfaction (<2.5)" if avg_job_sat < 2.5 else None
        ))
    
    # Environment satisfaction
    if env_sat_col and not env_sat_series.empty:
        avg_env_sat = env_sat_series.dropna().mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics",
            name="Avg Environment Satisfaction (Out of 4)",
            value=f"{avg_env_sat:.2f}",
            formula="Mean(EnvironmentSatisfaction)",
            source=f"`{env_sat_col}`",
            warnings="Low environment satisfaction (<2.5)" if avg_env_sat < 2.5 else None
        ))
    
    # Relationship satisfaction
    if rel_sat_col and not rel_sat_series.empty:
        avg_rel_sat = rel_sat_series.dropna().mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics",
            name="Avg Relationship Satisfaction (Out of 4)",
            value=f"{avg_rel_sat:.2f}",
            formula="Mean(RelationshipSatisfaction)",
            source=f"`{rel_sat_col}`",
            warnings="Low relationship satisfaction (<2.5)" if avg_rel_sat < 2.5 else None
        ))
    
    # Work-life balance
    if wlb_col and not wlb_series.empty:
        avg_wlb = wlb_series.dropna().mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics",
            name="Avg Work-Life Balance (Out of 4)",
            value=f"{avg_wlb:.2f}",
            formula="Mean(WorkLifeBalance)",
            source=f"`{wlb_col}`",
            warnings="Poor work-life balance (<2.5)" if avg_wlb < 2.5 else None
        ))
    
    # Overall engagement composite
    engagement_scores = []
    if job_sat_col and not job_sat_series.empty:
        engagement_scores.append(job_sat_series.dropna())
    if env_sat_col and not env_sat_series.empty:
        engagement_scores.append(env_sat_series.dropna())
    if rel_sat_col and not rel_sat_series.empty:
        engagement_scores.append(rel_sat_series.dropna())
    if wlb_col and not wlb_series.empty:
        engagement_scores.append(wlb_series.dropna())
    
    if engagement_scores:
        overall_engagement = pd.concat(engagement_scores).mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics",
            name="Overall Engagement Score",
            value=f"{overall_engagement:.2f} / 4.0",
            formula="Mean(All Satisfaction Metrics)",
            source="Composite",
            warnings="Low overall engagement (<2.5)" if overall_engagement < 2.5 else None
        ))
    
    return kpis
