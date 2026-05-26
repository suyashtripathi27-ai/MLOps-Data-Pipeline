"""
Absenteeism, attendance patterns, and workforce availability metrics.
GOVERNANCE: Operational metrics ONLY - No health/personal inference.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine
from utils.validator import SemanticValidator

# HR Industry Configuration
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_absenteeism_metrics(df, enable_debug=False):
    """Calculates absenteeism and attendance KPIs using KPIEngine."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Absence metrics are COUNT, not time
    employee_col, employee_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    absence_col, absence_series = engine.get_numeric(["absence_count", "absent_days", "total_absences"])
    unplanned_col, unplanned_series = engine.get_column(["unplanned_absence", "sick_leave", "unexpected_leave"])
    # Absence duration is ELAPSED TIME (days absent)
    absence_duration_col, absence_duration_series = engine.get_numeric(["absence_duration_days", "days_absent", "leave_duration"])
    absence_date_col, absence_date_series = engine.get_column(["absence_date", "leave_date", "absent_date"])
    attendance_col, attendance_series = engine.get_numeric(["attendance_rate", "attendance_pct", "present_rate"])
    
    if not employee_col:
        return kpis
    
    # Total employees
    total_employees = employee_series.nunique()
    
    kpis.append(engine.build_kpi(
        category="👥 Workforce",
        name="Total Employees Analyzed",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`"
    ))
    
    # Absence count
    if absence_col and not absence_series.empty:
        total_absences = absence_series.sum()
        avg_absence = absence_series.mean()
        
        kpis.append(engine.build_kpi(
            category="📅 Attendance",
            name="Total Absence Events",
            value=f"{total_absences:,.0f}",
            formula="Sum(Absence Count)",
            source=f"`{absence_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📅 Attendance",
            name="Avg Absences per Employee",
            value=f"{avg_absence:.2f}",
            formula="Mean(Absence Count)",
            source=f"`{absence_col}`",
            warnings="High absence frequency (>5/year)" if avg_absence > 5 else None
        ))
    
    # Unplanned absences
    if unplanned_col and not unplanned_series.empty:
        unplanned_mask = unplanned_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'unplanned'])
        unplanned_count = unplanned_mask.sum()
        unplanned_pct = (unplanned_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="📅 Attendance",
            name="Unplanned Absences",
            value=f"{unplanned_count:,} ({unplanned_pct:.1f}%)",
            formula="Count(Unplanned = True)",
            source=f"`{unplanned_col}`"
        ))
    
    # Absence duration (⏱️ ELAPSED TIME - days absent)
    if absence_duration_col and not absence_duration_series.empty:
        is_valid, reason = SemanticValidator.is_valid_duration(absence_duration_series)
        
        if is_valid:
            valid_duration = absence_duration_series.dropna()
            
            if not valid_duration.empty:
                total_days = valid_duration.sum()
                avg_days = valid_duration.mean()
                
                kpis.append(engine.build_kpi(
                    category="📅 Attendance",
                    name="Total Days Absent",
                    value=f"{total_days:,.0f} days",
                    formula="Sum(Absence Duration Days)",
                    source=f"`{absence_duration_col}`"
                ))
                
                kpis.append(engine.build_kpi(
                    category="📅 Attendance",
                    name="Avg Days per Absence",
                    value=f"{avg_days:.2f} days",
                    formula="Mean(Absence Duration Days)",
                    source=f"`{absence_duration_col}`"
                ))
    
    # Attendance rate
    if attendance_col and not attendance_series.empty:
        avg_attendance = attendance_series.mean()
        
        kpis.append(engine.build_kpi(
            category="📅 Attendance",
            name="Avg Attendance Rate",
            value=f"{avg_attendance:.2f}%",
            formula="Mean(Attendance Rate)",
            source=f"`{attendance_col}`",
            warnings="Low attendance (<90%)" if avg_attendance < 90 else None
        ))
    
    return kpis
