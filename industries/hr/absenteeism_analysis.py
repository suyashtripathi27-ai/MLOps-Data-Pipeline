"""
Absenteeism, attendance patterns, and workforce availability metrics.
GOVERNANCE: Operational metrics ONLY - No health/personal inference.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_absenteeism_metrics(df):
    """Calculates absenteeism and attendance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Absence metrics are COUNT, not time
    employee_col = first_column(df, ["employee_id", "emp_id", "staff_id"])
    absence_col = first_column(df, ["absence_count", "absent_days", "total_absences"])
    unplanned_col = first_column(df, ["unplanned_absence", "sick_leave", "unexpected_leave"])
    # Absence duration is ELAPSED TIME (days absent)
    absence_duration_col = first_column(df, ["absence_duration_days", "days_absent", "leave_duration"])
    absence_date_col = first_column(df, ["absence_date", "leave_date", "absent_date"])
    attendance_col = first_column(df, ["attendance_rate", "attendance_pct", "present_rate"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, absence_col, absence_duration_col, attendance_col] if col])
    
    # Total employees
    total_employees = df[employee_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Workforce",
        name="Total Employees Analyzed",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Absence count
    if absence_col and pd.api.types.is_numeric_dtype(df[absence_col]):
        total_absences = df[absence_col].sum()
        avg_absence = df[absence_col].mean()
        
        kpis.append(safe_kpi(
            category="📅 Attendance",
            name="Total Absence Events",
            value=f"{total_absences:,.0f}",
            formula="Sum(Absence Count)",
            source=f"`{absence_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📅 Attendance",
            name="Avg Absences per Employee",
            value=f"{avg_absence:.2f}",
            formula="Mean(Absence Count)",
            source=f"`{absence_col}`",
            confidence=conf,
            warnings="High absence frequency (>5/year)" if avg_absence > 5 else warns
        ))
    
    # Unplanned absences
    if unplanned_col:
        unplanned_mask = df[unplanned_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'unplanned'])
        unplanned_count = unplanned_mask.sum()
        unplanned_pct = (unplanned_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="📅 Attendance",
            name="Unplanned Absences",
            value=f"{unplanned_count:,} ({unplanned_pct:.1f}%)",
            formula="Count(Unplanned = True)",
            source=f"`{unplanned_col}`",
            confidence=conf,
            warnings="High unplanned absences (>30%)" if unplanned_pct > 30 else warns
        ))
    
    # Absence duration (⏱️ ELAPSED TIME - days away from work)
    if absence_duration_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[absence_duration_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[absence_duration_col]):
            valid_duration = df[absence_duration_col].dropna()
            
            if not valid_duration.empty:
                total_absent_days = valid_duration.sum()
                avg_absence_duration = valid_duration.mean()
                
                kpis.append(safe_kpi(
                    category="⏱️ Absence Duration",
                    name="Total Absence Days",
                    value=f"{total_absent_days:,.0f} days",
                    formula="Sum(Absence Duration)",
                    source=f"`{absence_duration_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="⏱️ Absence Duration",
                    name="Avg Absence Duration",
                    value=f"{avg_absence_duration:.1f} days",
                    formula="Mean(Absence Duration)",
                    source=f"`{absence_duration_col}`",
                    confidence=conf,
                    warnings="Long absence periods (>5 days avg)" if avg_absence_duration > 5 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="⏱️ Absence Duration",
                name="Absence Duration Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{absence_duration_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Attendance rate
    if attendance_col and pd.api.types.is_numeric_dtype(df[attendance_col]):
        valid_attendance = df[attendance_col].dropna()
        
        if not valid_attendance.empty:
            avg_attendance = valid_attendance.mean()
            
            kpis.append(safe_kpi(
                category="📅 Attendance",
                name="Avg Attendance Rate",
                value=f"{avg_attendance:.2f}%",
                formula="Mean(Attendance %)",
                source=f"`{attendance_col}`",
                confidence=conf,
                warnings="Low attendance (<90%)" if avg_attendance < 90 else warns
            ))
    
    # Absence rate calculation
    if absence_col:
        total_possible_days = total_employees * 250  # Approx working days per year
        total_absence_days = df[absence_col].sum()
        absence_rate = (total_absence_days / total_possible_days * 100) if total_possible_days > 0 else 0
        
        kpis.append(safe_kpi(
            category="📅 Attendance",
            name="Organizational Absence Rate",
            value=f"{absence_rate:.2f}%",
            formula="(Total Absence Days / Total Possible Days) * 100",
            source=f"`{absence_col}`",
            confidence=conf,
            warnings="High org absence rate (>5%)" if absence_rate > 5 else warns
        ))
    
    return kpis
