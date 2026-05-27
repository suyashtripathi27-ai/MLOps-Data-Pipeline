"""
Workplace safety, incidents, and safety metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_safety_metrics(df, enable_debug=False):
    """
    Calculates safety and incident KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    engine = KPIEngine(df, industry_config=MANUFACTURING_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Safety metrics
    incident_col, incident_series = engine.get_numeric(["incident_count", "safety_incidents", "near_misses"])
    injury_col, injury_series = engine.get_numeric(["injury_count", "lost_time_injuries", "injury_cases"])
    hours_col, hours_series = engine.get_numeric(["hours_worked", "worker_hours", "labor_hours"])
    severity_col, severity_series = engine.get_numeric(["severity_score", "incident_severity", "lost_days"])
    
    # ==========================================
    # 1. INCIDENT METRICS
    # ==========================================
    if incident_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        incident_clean = incident_series.dropna()
        
        if len(incident_clean) > 0:
            total_incidents = incident_clean.sum()
            
            warn_msg = "High incident rate - Review safety protocols (>5)" if total_incidents > 5 else "None"
            kpis.append(engine.build_kpi(
                category="🚨 Safety",
                name="Total Safety Incidents",
                value=f"{total_incidents:,.0f}",
                formula="Sum(Incidents)",
                source=f"`{incident_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("🚨 Safety", "Incidents", "All incident entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🚨 Safety", "Incidents", "Missing numeric 'incident_count' column."))
    
    # ==========================================
    # 2. INJURY METRICS
    # ==========================================
    if injury_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        injury_clean = injury_series.dropna()
        
        if len(injury_clean) > 0:
            total_injuries = injury_clean.sum()
            
            warn_msg = "Any injuries require immediate action" if total_injuries > 0 else "None"
            kpis.append(engine.build_kpi(
                category="🚨 Safety",
                name="Total Injuries",
                value=f"{total_injuries:,.0f}",
                formula="Sum(Injuries)",
                source=f"`{injury_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("🚨 Safety", "Injuries", "All injury entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🚨 Safety", "Injuries", "Missing numeric 'injury_count' column."))
    
    # ==========================================
    # 3. TRIR (Total Recordable Incident Rate)
    # ==========================================
    if incident_col is not None and hours_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        trir_clean = pd.concat([incident_series, hours_series], axis=1).dropna()
        
        if len(trir_clean) > 0:
            total_incidents = trir_clean[incident_col].sum()
            total_hours = trir_clean[hours_col].sum()
            
            if total_hours > 0:
                # TRIR = (Number of incidents / Total hours worked) × 200,000
                trir = (total_incidents / total_hours) * 200000
                
                warn_msg = "High TRIR - Investigate hazards (>5)" if trir > 5 else "None"
                kpis.append(engine.build_kpi(
                    category="🚨 Safety",
                    name="Total Recordable Incident Rate (TRIR)",
                    value=f"{trir:.2f}",
                    formula="(Total Incidents / Hours Worked) × 200,000",
                    source=f"`{incident_col}`, `{hours_col}`",
                    warnings=warn_msg
                ))
        else:
            kpis.append(engine.log_missing("🚨 Safety", "TRIR", "Missing valid incidents/hours data."))
    else:
        kpis.append(engine.log_missing("🚨 Safety", "TRIR", "Missing 'incident_count' or 'hours_worked' column."))
    
    # ==========================================
    # 4. SEVERITY ANALYSIS
    # ==========================================
    if severity_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        severity_clean = severity_series.dropna()
        
        if len(severity_clean) > 0:
            avg_severity = severity_clean.mean()
            total_lost_days = severity_clean.sum()
            
            kpis.append(engine.build_kpi(
                category="🚨 Safety",
                name="Avg Incident Severity",
                value=f"{avg_severity:.1f} days",
                formula="Mean(Severity / Lost Days)",
                source=f"`{severity_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="🚨 Safety",
                name="Total Lost Days",
                value=f"{total_lost_days:,.0f} days",
                formula="Sum(Lost Days)",
                source=f"`{severity_col}`"
            ))
        else:
            kpis.append(engine.log_missing("🚨 Safety", "Severity", "All severity entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🚨 Safety", "Severity", "Missing numeric 'severity_score' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
