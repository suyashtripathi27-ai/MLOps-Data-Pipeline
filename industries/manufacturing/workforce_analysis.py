"""
Labor, workforce productivity, and driver metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

LOGISTICS_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_workforce_metrics(df, enable_debug=False):
    """
    Calculates workforce and labor KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Workforce metrics - COUNT (headcount, hours), not time
    driver_col, driver_series = engine.get_column(["driver_id", "employee_id", "operator_id", "driver_name"])
    hours_col, hours_series = engine.get_numeric(["hours_worked", "driving_hours", "total_hours", "labor_hours"])
    trips_col, trips_series = engine.get_numeric(["trips_completed", "deliveries", "trips", "trip_count"])
    wage_col, wage_series = engine.get_numeric(["wage", "hourly_rate", "labor_cost", "driver_compensation"])
    safety_col, safety_series = engine.get_numeric(["safety_score", "driving_safety_rating", "incident_count"])
    
    # ==========================================
    # 1. DRIVER HEADCOUNT
    # ==========================================
    if driver_col is not None:
        total_drivers = driver_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="👥 Workforce",
            name="Total Active Drivers",
            value=f"{total_drivers:,}",
            formula="Count(Distinct Drivers)",
            source=f"`{driver_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Driver Headcount", "Missing 'driver_id' column."))
    
    # ==========================================
    # 2. LABOR HOURS
    # ==========================================
    if hours_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        hours_clean = hours_series.dropna()
        
        if len(hours_clean) > 0:
            total_hours = hours_clean.sum()
            avg_hours = hours_clean.mean()
            max_hours = hours_clean.max()
            
            kpis.append(engine.build_kpi(
                category="⏱️ Labor",
                name="Total Hours Worked",
                value=f"{total_hours:,.0f} hours",
                formula="Sum(Hours Worked)",
                source=f"`{hours_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="⏱️ Labor",
                name="Avg Hours per Driver",
                value=f"{avg_hours:.1f} hours",
                formula="Mean(Hours Worked)",
                source=f"`{hours_col}`"
            ))
            
            warn_msg = "High working hours - Fatigue risk (>12 hrs)" if max_hours > 12 else "None"
            kpis.append(engine.build_kpi(
                category="⏱️ Labor",
                name="Max Hours Worked",
                value=f"{max_hours:.1f} hours",
                formula="Max(Hours Worked)",
                source=f"`{hours_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("⏱️ Labor", "Hours Worked", "All hours entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⏱️ Labor", "Hours Worked", "Missing numeric 'hours_worked' column."))
    
    # ==========================================
    # 3. DRIVER PRODUCTIVITY
    # ==========================================
    if trips_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        trips_clean = trips_series.dropna()
        
        if len(trips_clean) > 0:
            total_trips = trips_clean.sum()
            avg_trips = trips_clean.mean()
            
            kpis.append(engine.build_kpi(
                category="👥 Workforce",
                name="Total Trips Completed",
                value=f"{total_trips:,.0f}

