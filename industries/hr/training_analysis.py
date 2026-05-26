"""
Training completion, skill development, and capability metrics.
GOVERNANCE: Operational capability metrics ONLY.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_training_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    emp_col, emp_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    trn_col, trn_series = engine.get_column(["training_id", "course_id", "program_id"])
    comp_col, comp_series = engine.get_column(["completed", "completion_flag", "passed"])
    dur_col, dur_series = engine.get_numeric(["training_hours", "hours", "duration_days"])
    cert_col, cert_series = engine.get_column(["certified", "certification_obtained", "cert_flag"])
    
    if emp_col is not None:
        kpis.append(engine.build_kpi(
            category="👥 Workforce", name="Total Employees Trained",
            value=f"{emp_series.nunique():,}", formula="Count(Distinct Employees)", source=f"`{emp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Employees Trained", "Missing employee ID."))
        return kpis

    if trn_col is not None:
        kpis.append(engine.build_kpi(
            category="📚 Training", name="Total Training Programs",
            value=f"{trn_series.nunique()}", formula="Count(Distinct Trainings)", source=f"`{trn_col}`"
        ))
    else:
        kpis.append(engine.log_missing("📚 Training", "Training Programs", "Missing training ID."))

    if comp_col is not None:
        comp_mask = comp_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'completed', 'passed'])
        comp_rate = (comp_mask.sum() / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="📚 Training", name="Training Completion Rate",
            value=f"{comp_rate:.2f}%", formula="(Completed / Total) * 100", 
            source=f"`{comp_col}`", warnings="Low completion (<80%)" if comp_rate < 80 else "None"
        ))
    else:
        kpis.append(engine.log_missing("📚 Training", "Completion Rate", "Missing completion flag."))

    if dur_col is not None and not dur_series.empty:
        is_valid, reason = engine.validate_business_rule("duration", dur_series)
        if is_valid:
            kpis.append(engine.build_kpi(
                category="📚 Training", name="Total Training Hours",
                value=f"{dur_series.sum():,.0f} hours", formula="Sum(Training Hours)", source=f"`{dur_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📚 Training", "Training Hours", f"Data corrupted: {reason}"))
    else:
        kpis.append(engine.log_missing("📚 Training", "Training Hours", "Missing duration data."))

    if cert_col is not None:
        cert_mask = cert_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'certified'])
        kpis.append(engine.build_kpi(
            category="🎯 Skills", name="Employees Certified",
            value=f"{cert_mask.sum():,}", formula="Count(Certified = True)", source=f"`{cert_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🎯 Skills", "Certifications", "Missing certification flag."))

    return kpis
