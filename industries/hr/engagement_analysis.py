"""
Employee engagement, satisfaction, and morale metrics.
GOVERNANCE: Operational aggregated metrics ONLY - No individual psychoanalysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_engagement_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    job_sat_col, job_sat_series = engine.get_numeric(["JobSatisfaction", "jobsatisfaction", "job_satisfaction", "satisfaction_score"])
    env_sat_col, env_sat_series = engine.get_numeric(["EnvironmentSatisfaction", "environmentsatisfaction", "environment_satisfaction"])
    rel_sat_col, rel_sat_series = engine.get_numeric(["RelationshipSatisfaction", "relationshipsatisfaction", "relationship_satisfaction"])
    wlb_col, wlb_series = engine.get_numeric(["WorkLifeBalance", "worklifebalance", "work_life_balance"])
    
    kpis.append(engine.build_kpi(
        category="👥 Engagement", name="Total Employees Assessed",
        value=f"{len(df):,}", formula="Total Rows", source="System"
    ))
    
    engagement_scores = []

    if job_sat_col is not None:
        valid_job = job_sat_series.dropna()
        engagement_scores.append(valid_job)
        avg_job_sat = valid_job.mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics", name="Avg Job Satisfaction (Out of 4)",
            value=f"{avg_job_sat:.2f}", formula="Mean(JobSatisfaction)", 
            source=f"`{job_sat_col}`", warnings="Low job satisfaction (<2.5)" if avg_job_sat < 2.5 else "None"
        ))
    else:
        kpis.append(engine.log_missing("📊 Engagement Metrics", "Job Satisfaction", "Missing job satisfaction scores."))

    if env_sat_col is not None:
        valid_env = env_sat_series.dropna()
        engagement_scores.append(valid_env)
        avg_env_sat = valid_env.mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics", name="Avg Environment Satisfaction (Out of 4)",
            value=f"{avg_env_sat:.2f}", formula="Mean(EnvironmentSatisfaction)", 
            source=f"`{env_sat_col}`", warnings="Low environment satisfaction (<2.5)" if avg_env_sat < 2.5 else "None"
        ))
    else:
        kpis.append(engine.log_missing("📊 Engagement Metrics", "Environment Satisfaction", "Missing environment scores."))

    if rel_sat_col is not None:
        valid_rel = rel_sat_series.dropna()
        engagement_scores.append(valid_rel)
        avg_rel_sat = valid_rel.mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics", name="Avg Relationship Satisfaction (Out of 4)",
            value=f"{avg_rel_sat:.2f}", formula="Mean(RelationshipSatisfaction)", 
            source=f"`{rel_sat_col}`", warnings="Low relationship satisfaction (<2.5)" if avg_rel_sat < 2.5 else "None"
        ))
    else:
        kpis.append(engine.log_missing("📊 Engagement Metrics", "Relationship Satisfaction", "Missing relationship scores."))

    if wlb_col is not None:
        valid_wlb = wlb_series.dropna()
        engagement_scores.append(valid_wlb)
        avg_wlb = valid_wlb.mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics", name="Avg Work-Life Balance (Out of 4)",
            value=f"{avg_wlb:.2f}", formula="Mean(WorkLifeBalance)", 
            source=f"`{wlb_col}`", warnings="Poor work-life balance (<2.5)" if avg_wlb < 2.5 else "None"
        ))
    else:
        kpis.append(engine.log_missing("📊 Engagement Metrics", "Work-Life Balance", "Missing work-life balance scores."))

    if engagement_scores:
        overall_engagement = pd.concat(engagement_scores).mean()
        kpis.append(engine.build_kpi(
            category="📊 Engagement Metrics", name="Overall Engagement Score",
            value=f"{overall_engagement:.2f} / 4.0", formula="Mean(All Satisfaction Metrics)", 
            source="Composite", warnings="Low overall engagement (<2.5)" if overall_engagement < 2.5 else "None"
        ))
    
    return kpis
