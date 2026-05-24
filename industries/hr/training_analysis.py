"""
Training completion, skill development, and capability metrics.
GOVERNANCE: Operational capability metrics ONLY.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_training_metrics(df):
    """Calculates training and skill development KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Training metrics
    employee_col = first_column(df, ["employee_id", "emp_id", "staff_id"])
    training_col = first_column(df, ["training_id", "course_id", "program_id"])
    completed_col = first_column(df, ["completed", "completion_flag", "passed"])
    # Training duration is ELAPSED TIME (hours/days of training)
    duration_col = first_column(df, ["training_hours", "hours", "duration_days"])
    completion_date_col = first_column(df, ["completion_date", "finish_date", "date_completed"])
    skill_col = first_column(df, ["skill_name", "skill", "competency"])
    certification_col = first_column(df, ["certified", "certification_obtained", "cert_flag"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, training_col, completed_col, duration_col, skill_col, certification_col] if col])
    
    # Total employees
    total_employees = df[employee_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Workforce",
        name="Total Employees Trained",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Training programs
    if training_col:
        total_trainings = df[training_col].nunique()
        
        kpis.append(safe_kpi(
            category="📚 Training",
            name="Total Training Programs",
            value=f"{total_trainings}",
            formula="Count(Distinct Trainings)",
            source=f"`{training_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Completion rate
    if completed_col:
        completed_mask = df[completed_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'completed', 'passed'])
        completed_count = completed_mask.sum()
        completion_rate = (completed_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="📚 Training",
            name="Training Completion Count",
            value=f"{completed_count:,}",
            formula="Count(Completed = True)",
            source=f"`{completed_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📚 Training",
            name="Training Completion Rate",
            value=f"{completion_rate:.2f}%",
            formula="(Completed / Total) * 100",
            source=f"`{completed_col}`",
            confidence=conf,
            warnings="Low completion (<80%)" if completion_rate < 80 else warns
        ))
    
    # Training duration (⏱️ ELAPSED TIME - hours spent in training)
    if duration_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[duration_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[duration_col]):
            valid_duration = df[duration_col].dropna()
            
            if not valid_duration.empty:
                total_hours = valid_duration.sum()
                avg_hours = valid_duration.mean()
                
                kpis.append(safe_kpi(
                    category="⏱️ Training Investment",
                    name="Total Training Hours",
                    value=f"{total_hours:,.0f} hours",
                    formula="Sum(Training Hours)",
                    source=f"`{duration_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="⏱️ Training Investment",
                    name="Avg Training Hours per Employee",
                    value=f"{avg_hours:.1f} hours",
                    formula="Mean(Training Hours)",
                    source=f"`{duration_col}`",
                    confidence=conf,
                    warnings="Low training investment (<20 hrs/yr)" if avg_hours < 20 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="⏱️ Training Investment",
                name="Training Duration Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{duration_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Certification
    if certification_col:
        certified_mask = df[certification_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'certified'])
        certified_count = certified_mask.sum()
        certification_rate = (certified_count / total_employees * 100) if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="📚 Training",
            name="Certified Employees",
            value=f"{certified_count:,} ({certification_rate:.1f}%)",
            formula="Count(Certified) / Total Employees",
            source=f"`{certification_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Skills coverage
    if skill_col:
        unique_skills = df[skill_col].nunique()
        
        kpis.append(safe_kpi(
            category="📚 Training",
            name="Unique Skills Trained",
            value=f"{unique_skills}",
            formula="Count(Distinct Skills)",
            source=f"`{skill_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
