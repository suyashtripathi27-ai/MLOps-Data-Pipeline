"""
Training completion, skill development, and capability metrics.
GOVERNANCE: Operational capability metrics ONLY.
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

def calc_training_metrics(df, enable_debug=False):
    """Calculates training and skill development KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Training metrics
    employee_col, employee_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    training_col, training_series = engine.get_column(["training_id", "course_id", "program_id"])
    completed_col, completed_series = engine.get_column(["completed", "completion_flag", "passed"])
    # Training duration is ELAPSED TIME (hours/days of training)
    duration_col, duration_series = engine.get_numeric(["training_hours", "hours", "duration_days"])
    completion_date_col, completion_date_series = engine.get_column(["completion_date", "finish_date", "date_completed"])
    skill_col, skill_series = engine.get_column(["skill_name", "skill", "competency"])
    certification_col, certification_series = engine.get_column(["certified", "certification_obtained", "cert_flag"])
    
    if not employee_col:
        return kpis
    
    # Total employees
    total_employees = employee_series.nunique()
    
    kpis.append(engine.build_kpi(
        category="👥 Workforce",
        name="Total Employees Trained",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`"
    ))
    
    # Training programs
    if training_col:
        total_trainings = training_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="📚 Training",
            name="Total Training Programs",
            value=f"{total_trainings}",
            formula="Count(Distinct Trainings)",
            source=f"`{training_col}`"
        ))
    
    # Completion rate
    if completed_col and not completed_series.empty:
        completed_mask = completed_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'completed', 'passed'])
        completed_count = completed_mask.sum()
        completion_rate = (completed_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="📚 Training",
            name="Training Completion Count",
            value=f"{completed_count:,}",
            formula="Count(Completed = True)",
            source=f"`{completed_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📚 Training",
            name="Training Completion Rate",
            value=f"{completion_rate:.2f}%",
            formula="(Completed / Total) * 100",
            source=f"`{completed_col}`",
            warnings="Low completion (<80%)" if completion_rate < 80 else None
        ))
    
    # Training duration (⏱️ ELAPSED TIME - hours spent in training)
    if duration_col and not duration_series.empty:
        is_valid, reason = SemanticValidator.is_valid_duration(duration_series)
        
        if is_valid:
            valid_duration = duration_series.dropna()
            
            if not valid_duration.empty:
                total_hours = valid_duration.sum()
                avg_hours = valid_duration.mean()
                
                kpis.append(engine.build_kpi(
                    category="📚 Training",
                    name="Total Training Hours",
                    value=f"{total_hours:,.0f} hours",
                    formula="Sum(Training Hours)",
                    source=f"`{duration_col}`"
                ))
                
                kpis.append(engine.build_kpi(
                    category="📚 Training",
                    name="Avg Training Hours per Person",
                    value=f"{avg_hours:.2f} hours",
                    formula="Mean(Training Hours)",
                    source=f"`{duration_col}`"
                ))
    
    # Skills developed
    if skill_col:
        unique_skills = skill_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="🎯 Skills",
            name="Unique Skills Developed",
            value=f"{unique_skills}",
            formula="Count(Distinct Skills)",
            source=f"`{skill_col}`"
        ))
    
    # Certifications
    if certification_col and not certification_series.empty:
        certified_mask = certification_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'certified'])
        certified_count = certified_mask.sum()
        certification_rate = (certified_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🎯 Skills",
            name="Employees Certified",
            value=f"{certified_count:,} ({certification_rate:.1f}%)",
            formula="Count(Certified = True)",
            source=f"`{certification_col}`"
        ))
    
    return kpis
