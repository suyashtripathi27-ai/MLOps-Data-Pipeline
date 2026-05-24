"""
Compensation, payroll, and benefits metrics.
GOVERNANCE: EXTREMELY SENSITIVE - Operational payroll metrics ONLY.
DO NOT infer discrimination, protected attributes, or demographic conclusions.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_compensation_metrics(df):
    """Calculates compensation and payroll KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Compensation metrics - OPERATIONAL only
    employee_col = first_column(df, ["employee_id", "emp_id", "staff_id"])
    salary_col = first_column(df, ["salary", "base_salary", "annual_salary"])
    bonus_col = first_column(df, ["bonus", "bonus_amount", "performance_bonus"])
    overtime_col = first_column(df, ["overtime_cost", "overtime_hours", "extra_pay"])
    benefits_col = first_column(df, ["benefits_cost", "healthcare_cost", "benefits_value"])
    
    if not employee_col or not salary_col:
        return kpis
    
    # Salary is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[salary_col]):
        kpis.append(safe_kpi(
            category="💰 Compensation",
            name="Compensation Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{salary_col}`",
            confidence="Low",
            warnings="Salary column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, salary_col, bonus_col, overtime_col, benefits_col] if col])
    
    # Total headcount
    total_employees = df[employee_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Compensation",
        name="Total Employees",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Salary metrics
    valid_salary = df[salary_col].dropna()
    
    if not valid_salary.empty:
        total_payroll = valid_salary.sum()
        avg_salary = valid_salary.mean()
        median_salary = valid_salary.median()
        
        kpis.append(safe_kpi(
            category="💰 Compensation",
            name="Total Payroll",
            value=f"${total_payroll:,.2f}",
            formula="Sum(Salary)",
            source=f"`{salary_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Compensation",
            name="Avg Salary",
            value=f"${avg_salary:,.2f}",
            formula="Mean(Salary)",
            source=f"`{salary_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Compensation",
            name="Median Salary",
            value=f"${median_salary:,.2f}",
            formula="Median(Salary)",
            source=f"`{salary_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Bonus metrics
    if bonus_col and pd.api.types.is_numeric_dtype(df[bonus_col]):
        valid_bonus = df[bonus_col].dropna()
        
        if not valid_bonus.empty:
            total_bonus = valid_bonus.sum()
            avg_bonus = valid_bonus.mean()
            bonus_rate = (len(valid_bonus[valid_bonus > 0]) / total_employees * 100) if total_employees > 0 else 0
            
            kpis.append(safe_kpi(
                category="💰 Compensation",
                name="Total Bonus Paid",
                value=f"${total_bonus:,.2f}",
                formula="Sum(Bonus)",
                source=f"`{bonus_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💰 Compensation",
                name="Avg Bonus Amount",
                value=f"${avg_bonus:,.2f}",
                formula="Mean(Bonus)",
                source=f"`{bonus_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💰 Compensation",
                name="Employees Receiving Bonus",
                value=f"{bonus_rate:.1f}%",
                formula="(Employees with Bonus > 0 / Total) * 100",
                source=f"`{bonus_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Overtime costs
    if overtime_col and pd.api.types.is_numeric_dtype(df[overtime_col]):
        valid_ot = df[overtime_col].dropna()
        
        if not valid_ot.empty:
            total_ot = valid_ot.sum()
            avg_ot = valid_ot.mean()
            
            kpis.append(safe_kpi(
                category="💰 Payroll",
                name="Total Overtime Cost",
                value=f"${total_ot:,.2f}",
                formula="Sum(Overtime Cost)",
                source=f"`{overtime_col}`",
                confidence=conf,
                warnings="High overtime spending" if total_ot > total_payroll * 0.10 else warns
            ))
            
            kpis.append(safe_kpi(
                category="💰 Payroll",
                name="Avg Overtime per Employee",
                value=f"${avg_ot:,.2f}",
                formula="Mean(Overtime Cost)",
                source=f"`{overtime_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Benefits costs
    if benefits_col and pd.api.types.is_numeric_dtype(df[benefits_col]):
        valid_benefits = df[benefits_col].dropna()
        
        if not valid_benefits.empty:
            total_benefits = valid_benefits.sum()
            avg_benefits = valid_benefits.mean()
            
            kpis.append(safe_kpi(
                category="💰 Benefits",
                name="Total Benefits Cost",
                value=f"${total_benefits:,.2f}",
                formula="Sum(Benefits Cost)",
                source=f"`{benefits_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💰 Benefits",
                name="Avg Benefits per Employee",
                value=f"${avg_benefits:,.2f}",
                formula="Mean(Benefits Cost)",
                source=f"`{benefits_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Total compensation
    if salary_col and benefits_col:
        total_comp = total_payroll + (total_benefits if benefits_col and 'total_benefits' in locals() else 0)
        
        kpis.append(safe_kpi(
            category="💰 Compensation",
            name="Total Compensation Cost",
            value=f"${total_comp:,.2f}",
            formula="Total Payroll + Benefits",
            source=f"`{salary_col}`, `{benefits_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
