"""
Compensation, payroll, and benefits metrics.
GOVERNANCE: EXTREMELY SENSITIVE - Operational payroll metrics ONLY.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_compensation_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    emp_col, emp_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    sal_col, sal_series = engine.get_numeric(["salary", "base_salary", "annual_salary"])
    bon_col, bon_series = engine.get_numeric(["bonus", "bonus_amount", "performance_bonus"])
    ot_col, ot_series = engine.get_numeric(["overtime_cost", "overtime_hours", "extra_pay"])
    ben_col, ben_series = engine.get_numeric(["benefits_cost", "healthcare_cost", "benefits_value"])
    
    if emp_col is not None:
        kpis.append(engine.build_kpi(
            category="👥 Compensation", name="Total Employees",
            value=f"{emp_series.nunique():,}", formula="Count(Distinct Employees)", source=f"`{emp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Compensation", "Total Employees", "Missing employee ID."))
        return kpis 

    if sal_col is not None:
        valid_salary = sal_series.dropna()
        kpis.append(engine.build_kpi(
            category="💰 Compensation", name="Total Payroll",
            value=f"${valid_salary.sum():,.2f}", formula="Sum(Salary)", source=f"`{sal_col}`", sensitivity="HR_SENSITIVE"
        ))
        kpis.append(engine.build_kpi(
            category="💰 Compensation", name="Avg Salary",
            value=f"${valid_salary.mean():,.2f}", formula="Mean(Salary)", source=f"`{sal_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💰 Compensation", "Salary Metrics", "Missing base salary data."))

    if bon_col is not None:
        kpis.append(engine.build_kpi(
            category="💰 Compensation", name="Total Bonuses",
            value=f"${bon_series.sum():,.2f}", formula="Sum(Bonus)", source=f"`{bon_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💰 Compensation", "Bonuses", "Missing bonus data."))

    if ot_col is not None:
        kpis.append(engine.build_kpi(
            category="⏱️ Overtime", name="Total Overtime Cost",
            value=f"${ot_series.sum():,.2f}", formula="Sum(Overtime)", source=f"`{ot_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⏱️ Overtime", "Overtime Metrics", "Missing overtime cost data."))

    if ben_col is not None:
        kpis.append(engine.build_kpi(
            category="🎁 Benefits", name="Total Benefits Cost",
            value=f"${ben_series.sum():,.2f}", formula="Sum(Benefits)", source=f"`{ben_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🎁 Benefits", "Benefits Metrics", "Missing benefits data."))

    return kpis
