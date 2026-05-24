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
    
    # Engagement metrics - OPERATIONAL signals only
    employee_col = first_column(df, ["employee_id", "emp_id", "staff_id"])
    engagement_col = first_column(df, ["engagement_score", "engagement_rating", "engagement_level"])
    satisfaction_col = first_column(df, ["satisfaction_score", "job_satisfaction", "satisfaction_rating"])
    eNPS_col = first_column(df, ["eNPS", "employee_nps", "nps_score"])
    survey_col = first_column(df, ["pulse_score", "survey_response", "feedback_score"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, engagement_col, satisfaction_col, eNPS_col, survey_col] if col])
    
    # Total employees surveyed
    total_employees = df[employee_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Engagement",
        name="Total Employees Assessed",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Engagement score
    if engagement_col and pd.api.types.is_numeric_dtype(df[engagement_col]):
        valid_engagement = df[engagement_col].dropna()
        
        if not valid_engagement.empty:
            avg_engagement = valid_engagement.mean()
            
            kpis.append(safe_kpi(
                category="📊 Engagement Metrics",
                name="Avg Engagement Score",
                value=f"{avg_engagement:.2f}",
                formula="Mean(Engagement Score)",
                source=f"`{engagement_col}`",
                confidence=conf,
                warnings="Low engagement (<3.0 on 5-scale)" if avg_engagement < 3.0 else warns
            ))
            
            # Score distribution
            high_engagement = (valid_engagement >= 4).sum()
            low_engagement = (valid_engagement <= 2).sum()
            
            kpis.append(safe_kpi(
                category="📊 Engagement Metrics",
                name="Highly Engaged (%)",
                value=f"{high_engagement/len(valid_engagement)*100:.1f}%",
                formula="Count(Score >= 4) / Total",
                source=f"`{engagement_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="📊 Engagement Metrics",
                name="Low Engagement (%)",
                value=f"{low_engagement/len(valid_engagement)*100:.1f}%",
                formula="Count(Score <= 2) / Total",
                source=f"`{engagement_col}`",
                confidence=conf,
                warnings="Significant low engagement" if low_engagement/len(valid_engagement) > 0.2 else warns
            ))
    
    # Satisfaction
    if satisfaction_col and pd.api.types.is_numeric_dtype(df[satisfaction_col]):
        valid_satisfaction = df[satisfaction_col].dropna()
        
        if not valid_satisfaction.empty:
            avg_satisfaction = valid_satisfaction.mean()
            
            kpis.append(safe_kpi(
                category="📊 Engagement Metrics",
                name="Avg Satisfaction Score",
                value=f"{avg_satisfaction:.2f}",
                formula="Mean(Satisfaction Score)",
                source=f"`{satisfaction_col}`",
                confidence=conf,
                warnings="Low satisfaction" if avg_satisfaction < 3.0 else warns
            ))
    
    # eNPS (Employee Net Promoter Score)
    if eNPS_col and pd.api.types.is_numeric_dtype(df[eNPS_col]):
        valid_nps = df[eNPS_col].dropna()
        
        if not valid_nps.empty:
            avg_nps = valid_nps.mean()
            
            kpis.append(safe_kpi(
                category="📊 Engagement Metrics",
                name="Avg eNPS",
                value=f"{avg_nps:.2f}",
                formula="Mean(eNPS Score)",
                source=f"`{eNPS_col}`",
                confidence=conf,
                warnings="Low eNPS (<30)" if avg_nps < 30 else warns
            ))
    
    # Pulse survey
    if survey_col and pd.api.types.is_numeric_dtype(df[survey_col]):
        valid_survey = df[survey_col].dropna()
        
        if not valid_survey.empty:
            avg_survey = valid_survey.mean()
            response_rate = (len(valid_survey) / total_employees * 100) if total_employees > 0 else 0
            
            kpis.append(safe_kpi(
                category="📊 Engagement Metrics",
                name="Pulse Survey Score",
                value=f"{avg_survey:.2f}",
                formula="Mean(Pulse Score)",
                source=f"`{survey_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="📊 Engagement Metrics",
                name="Survey Response Rate",
                value=f"{response_rate:.1f}%",
                formula="(Responses / Total Employees) * 100",
                source=f"`{survey_col}`, `{employee_col}`",
                confidence=conf,
                warnings="Low participation (<60%)" if response_rate < 60 else warns
            ))
    
    return kpis
