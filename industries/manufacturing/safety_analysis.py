"""
Workplace safety, incidents, and safety metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_safety_metrics(df):
    """Calculates safety and incident KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Safety metrics
    incident_col = first_column(df, ["incident_count", "safety_incidents", "near_misses"])
    injury_col = first_column(df, ["injury_count", "lost_time_injuries", "injury_cases"])
    hours_col = first_column(df, ["hours_worked", "worker_hours", "labor_hours"])
    severity_col = first_column(df, ["severity_score", "incident_severity", "lost_days"])
    
    if not incident_col and not injury_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [incident_col, injury_col, hours_col, severity_col] if col])
    
    # Incident metrics
    if incident_col and pd.api.types.is_numeric_dtype(df[incident_col]):
        total_incidents = df[incident_col].sum()
        
        kpis.append(safe_kpi(
            category="🚨 Safety",
            name="Total Safety Incidents",
            value=f"{total_incidents:,.0f}",
            formula="Sum(Incidents)",
            source=f"`{incident_col}`",
            confidence=conf,
            warnings="High incident rate - Review safety protocols" if total_incidents > 5 else warns
        ))
    
    # Injury metrics
    if injury_col and pd.api.types.is_numeric_dtype(df[injury_col]):
        total_injuries = df[injury_col].sum()
        
        kpis.append(safe_kpi(
            category="🚨 Safety",
            name="Total Injuries",
            value=f"{total_injuries:,.0f}",
            formula="Sum(Injuries)",
            source=f"`{injury_col}`",
            confidence=conf,
            warnings="Any injuries require immediate action" if total_injuries > 0 else warns
        ))
    
    # TRIR (Total Recordable Incident Rate)
    if incident_col and hours_col and pd.api.types.is_numeric_dtype(df[incident_col]) and pd.api.types.is_numeric_dtype(df[hours_col]):
        total_incidents = df[incident_col].sum()
        total_hours = df[hours_col].sum()
        
        # TRIR = (Number of incidents / Total hours worked) × 200,000
        if total_hours > 0:
            trir = (total_incidents / total_hours) * 200000
            
            kpis.append(safe_kpi(
                category="🚨 Safety",
                name="Total Recordable Incident Rate (TRIR)",
                value=f"{trir:.2f}",
                formula="(Total Incidents / Hours Worked) × 200,000",
                source=f"`{incident_col}`, `{hours_col}`",
                confidence=conf,
                warnings="High TRIR - Investigate hazards" if trir > 5 else warns
            ))
    
    # Severity analysis
    if severity_col and pd.api.types.is_numeric_dtype(df[severity_col]):
        valid_severity = df[severity_col].dropna()
        
        if not valid_severity.empty:
            avg_severity = valid_severity.mean()
            total_lost_days = valid_severity.sum()
            
            kpis.append(safe_kpi(
                category="🚨 Safety",
                name="Avg Incident Severity",
                value=f"{avg_severity:.1f} days",
                formula="Mean(Severity / Lost Days)",
                source=f"`{severity_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🚨 Safety",
                name="Total Lost Days",
                value=f"{total_lost_days:,.0f} days",
                formula="Sum(Lost Days)",
                source=f"`{severity_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
