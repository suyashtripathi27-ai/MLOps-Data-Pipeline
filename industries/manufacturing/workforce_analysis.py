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
                value=f"{total_trips:,.0f}",
                formula="Sum(Trips)",
                source=f"`{trips_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="👥 Workforce",
                name="Avg Trips per Driver",
                value=f"{avg_trips:.2f}",
                formula="Mean(Trips per Driver)",
                source=f"`{trips_col}`"
            ))
        else:
            kpis.append(engine.log_missing("👥 Workforce", "Productivity", "All trips entries are missing/null."))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Productivity", "Missing numeric 'trips_completed' column."))
    
    # ==========================================
    # 4. TRIPS PER HOUR (EFFICIENCY)
    # ==========================================
    if trips_col is not None and hours_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        efficiency_clean = pd.concat([trips_series, hours_series], axis=1).dropna()
        
        if len(efficiency_clean) > 0:
            total_trips = efficiency_clean[trips_col].sum()
            total_hours = efficiency_clean[hours_col].sum()
            
            if total_hours > 0:
                trips_per_hour = total_trips / total_hours
                
                kpis.append(engine.build_kpi(
                    category="👥 Workforce",
                    name="Trips per Hour",
                    value=f"{trips_per_hour:.2f} trips/hour",
                    formula="Total Trips / Total Hours",
                    source=f"`{trips_col}`, `{hours_col}`"
                ))
        else:
            kpis.append(engine.log_missing("👥 Workforce", "Efficiency", "Missing valid trips/hours data."))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Efficiency", "Missing 'trips_completed' or 'hours_worked' column."))
    
    # ==========================================
    # 5. LABOR COST
    # ==========================================
    if wage_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        wage_clean = wage_series.dropna()
        
        if len(wage_clean) > 0:
            total_wages = wage_clean.sum()
            avg_wage = wage_clean.mean()
            
            kpis.append(engine.build_kpi(
                category="💰 Labor Cost",
                name="Total Labor Cost",
                value=f"${total_wages:,.2f}",
                formula="Sum(Wages)",
                source=f"`{wage_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Labor Cost",
                name="Avg Labor Cost per Driver",
                value=f"${avg_wage:,.2f}",
                formula="Mean(Wages)",
                source=f"`{wage_col}`"
            ))
            
            # ==========================================
            # 6. LABOR COST PER TRIP
            # ==========================================
            if trips_col is not None:
                # FIX: Drop NaN values BEFORE calculating
                cost_trips_clean = pd.concat([wage_series, trips_series], axis=1).dropna()
                
                if len(cost_trips_clean) > 0:
                    total_wages = cost_trips_clean[wage_col].sum()
                    total_trips = cost_trips_clean[trips_col].sum()
                    
                    if total_trips > 0:
                        labor_cost_per_trip = total_wages / total_trips
                        
                        kpis.append(engine.build_kpi(
                            category="💰 Labor Cost",
                            name="Labor Cost per Trip",
                            value=f"${labor_cost_per_trip:,.2f}",
                            formula="Total Labor Cost / Total Trips",
                            source=f"`{wage_col}`, `{trips_col}`"
                        ))
                else:
                    kpis.append(engine.log_missing("💰 Labor Cost", "Cost per Trip", "Missing valid wages/trips data."))
            else:
                kpis.append(engine.log_missing("💰 Labor Cost", "Cost per Trip", "Missing 'trips_completed' column."))
        else:
            kpis.append(engine.log_missing("💰 Labor Cost", "Labor Cost", "All wage entries are missing/null."))
    else:
        kpis.append(engine.log_missing("💰 Labor Cost", "Labor Cost", "Missing numeric 'wage' column."))
    
    # ==========================================
    # 7. DRIVER SAFETY
    # ==========================================
    if safety_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        safety_clean = safety_series.dropna()
        
        if len(safety_clean) > 0:
            avg_safety = safety_clean.mean()
            min_safety = safety_clean.min()
            
            warn_msg = "Low safety score - Review driver performance (<80)" if avg_safety < 80 else "None"
            kpis.append(engine.build_kpi(
                category="🚨 Safety",
                name="Avg Driver Safety Score",
                value=f"{avg_safety:.2f}",
                formula="Mean(Safety Score)",
                source=f"`{safety_col}`",
                warnings=warn_msg
            ))
            
            kpis.append(engine.build_kpi(
                category="🚨 Safety",
                name="Min Driver Safety Score",
                value=f"{min_safety:.2f}",
                formula="Min(Safety Score)",
                source=f"`{safety_col}`",
                warnings="Critical: Very low safety score" if min_safety < 60 else "None"
            ))
        else:
            kpis.append(engine.log_missing("🚨 Safety", "Safety Score", "All safety entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🚨 Safety", "Safety Score", "Missing numeric 'safety_score' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
