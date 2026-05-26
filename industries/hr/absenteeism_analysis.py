"""
Absenteeism, attendance patterns, and workforce availability metrics.
GOVERNANCE: Operational metrics ONLY - No health/personal inference.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# HR Industry Configuration
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_absenteeism_metrics(df, enable_debug=False):
    """Calculates absenteeism and attendance KPIs using KPIEngine."""
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
        
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    emp_col, emp_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    abs_col, abs_series = engine.get_numeric(["absence_count", "absent_days", "total_absences"])
    unp_col, unp_series = engine.get_column(["unplanned_absence", "sick_leave", "unexpected_leave"])
    dur_col, dur_series = engine.get_numeric(["absence_duration_days", "days_absent", "leave_duration"])
    att_col, att_series = engine.get_numeric(["attendance_rate", "attendance_pct", "present_rate"])
    
    # ==========================================
    # 1. WORKFORCE BASELINE
    # ==========================================
    if emp_col is not None:
        total_employees = emp_series.nunique()
        kpis.append(engine.build_kpi(
            category="👥 Workforce", name="Total Employees Analyzed",
            value=f"{total_employees:,}", formula="Count(Distinct Employees)", source=f"`{emp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Total Employees", "Missing 'employee_id' column."))
        return kpis 
    
    # ==========================================
    # 2. ABSENCE FREQUENCY
    # ==========================================
    if abs_col is not None:
        total_absences = abs_series.sum()
        avg_absence = abs_series.mean()
        warn_msg = "High absence frequency (>5/year)" if avg_absence > 5 else "None"
        
        kpis.append(engine.build_kpi(
            category="📅 Attendance", name="Total Absence Events",
            value=f"{total_absences:,.0f}", formula="Sum(Absence Count)", source=f"`{abs_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="📅 Attendance", name="Avg Absences per Employee",
            value=f"{avg_absence:.2f}", formula="Mean(Absence Count)", 
            source=f"`{abs_col}`", warnings=warn_msg
        ))
    else:
        kpis.append(engine.log_missing("📅 Attendance", "Absence Frequency", "Missing 'absence_count' column."))
    
    # ==========================================
    # 3. UNPLANNED ABSENCES
    # ==========================================
    if unp_col is not None:
        unp_mask = unp_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'unplanned'])
        unp_count = unp_mask.sum()
        unp_pct = (unp_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="📅 Attendance", name="Unplanned Absences",
            value=f"{unp_count:,} ({unp_pct:.1f}%)", formula="Count(Unplanned = True)", source=f"`{unp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("📅 Attendance", "Unplanned Absences", "Missing 'unplanned_absence' flag."))
    
    # ==========================================
    # 4. ABSENCE DURATION (Using Engine Business Rules!)
    # ==========================================
    if dur_col is not None:
        is_valid, reason = engine.validate_business_rule("duration", dur_series)
        
        if is_valid:
            total_days = dur_series.sum()
            kpis.append(engine.build_kpi(
                category="📅 Attendance", name="Total Days Absent",
                value=f"{total_days:,.0f} days", formula="Sum(Duration)", source=f"`{dur_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="📅 Attendance", name="Avg Days per Absence",
                value=f"{dur_series.mean():.2f} days", formula="Mean(Duration)", source=f"`{dur_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📅 Attendance", "Absence Duration", f"Data corruption: {reason}"))
    else:
        kpis.append(engine.log_missing("📅 Attendance", "Absence Duration", "Missing duration column."))
    
    # ==========================================
    # 5. ATTENDANCE RATE
    # ==========================================
    if att_col is not None:
        avg_attendance = att_series.mean()
        warn_msg = "Low attendance (<90%)" if avg_attendance < 90 else "None"
        
        kpis.append(engine.build_kpi(
            category="📅 Attendance", name="Avg Attendance Rate",
            value=f"{avg_attendance:.2f}%", formula="Mean(Attendance Rate)", 
            source=f"`{att_col}`", warnings=warn_msg
        ))
    else:
        kpis.append(engine.log_missing("📅 Attendance", "Attendance Rate", "Missing 'attendance_rate' column."))
    
    if enable_debug:
        engine.print_execution_log()
        
    return kpis
