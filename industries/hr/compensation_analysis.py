"""
Compensation, payroll, and benefits metrics.
GOVERNANCE: EXTREMELY SENSITIVE - Operational payroll metrics ONLY.
DO NOT infer discrimination, protected attributes, or demographic conclusions.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# HR Industry Configuration  
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_compensation_metrics(df, enable_debug=False):
    """Calculates compensation and payroll KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Compensation metrics - OPERATIONAL only
    employee_col, employee_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    salary_col, salary_series = engine.get_numeric(["salary", "base_salary", "annual_salary"])
    bonus_col, bonus_series = engine.get_numeric(["bonus", "bonus_amount", "performance_bonus"])
    overtime_col, overtime_series = engine.get_numeric(["overtime_cost", "overtime_hours", "extra_pay"])
    benefits_col, benefits_series = engine.get_numeric(["benefits_cost", "healthcare_cost", "benefits_value"])
    
    if not employee_col or not salary_col:
        return kpis
    
    # Total headcount
    total_employees = employee_series.nunique()
    
    kpis.append(engine.build_kpi(
        category="👥 Compensation",
        name="Total Employees",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`"
    ))
    
    # Salary metrics
    if salary_col and not salary_series.empty:
        valid_salary = salary_series.dropna()
        
        if not valid_salary.empty:
            total_payroll = valid_salary.sum()
            avg_salary = valid_salary.mean()
            median_salary = valid_salary.median()
            
            kpis.append(engine.build_kpi(
                category="💰 Compensation",
                name="Total Payroll",
                value=f"${total_payroll:,.2f}",
                formula="Sum(Salary)",
                source=f"`{salary_col}`",
                sensitivity="HR_SENSITIVE"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Compensation",
                name="Avg Salary",
                value=f"${avg_salary:,.2f}",
                formula="Mean(Salary)",
                source=f"`{salary_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Compensation",
                name="Median Salary",
                value=f"${median_salary:,.2f}",
                formula="Median(Salary)",
                source=f"`{salary_col}`"
            ))
    
    # Bonus metrics
    if bonus_col and not bonus_series.empty:
        valid_bonus = bonus_series.dropna()
        
        if not valid_bonus.empty:
            total_bonus = valid_bonus.sum()
            avg_bonus = valid_bonus.mean()
            
            kpis.append(engine.build_kpi(
                category="💰 Compensation",
                name="Total Bonuses",
                value=f"${total_bonus:,.2f}",
                formula="Sum(Bonus)",
                source=f"`{bonus_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Compensation",
                name="Avg Bonus",
                value=f"${avg_bonus:,.2f}",
                formula="Mean(Bonus)",
                source=f"`{bonus_col}`"
            ))
    
    # Overtime
    if overtime_col and not overtime_series.empty:
        valid_overtime = overtime_series.dropna()
        
        if not valid_overtime.empty:
            total_overtime = valid_overtime.sum()
            avg_overtime = valid_overtime.mean()
            
            kpis.append(engine.build_kpi(
                category="⏱️ Overtime",
                name="Total Overtime Cost",
                value=f"${total_overtime:,.2f}",
                formula="Sum(Overtime)",
                source=f"`{overtime_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="⏱️ Overtime",
                name="Avg Overtime per Employee",
                value=f"${avg_overtime:,.2f}",
                formula="Mean(Overtime)",
                source=f"`{overtime_col}`"
            ))
    
    # Benefits
    if benefits_col and not benefits_series.empty:
        valid_benefits = benefits_series.dropna()
        
        if not valid_benefits.empty:
            total_benefits = valid_benefits.sum()
            avg_benefits = valid_benefits.mean()
            
            kpis.append(engine.build_kpi(
                category="🎁 Benefits",
                name="Total Benefits Cost",
                value=f"${total_benefits:,.2f}",
                formula="Sum(Benefits)",
                source=f"`{benefits_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="🎁 Benefits",
                name="Avg Benefits per Employee",
                value=f"${avg_benefits:,.2f}",
                formula="Mean(Benefits)",
                source=f"`{benefits_col}`"
            ))
    
    return kpis
