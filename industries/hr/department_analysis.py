"""
Calculates HR department headcount, attrition concentration, and salary distribution.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# HR industry configuration
HR_CONFIG = {
    "missing_data_threshold": 5,        
    "score_deduction_for_warning": 15,  
    "low_confidence_threshold": 30,    
}

def calc_department_metrics(df, enable_debug=False):
    """
    Calculate departmental headcount and attrition KPIs.
    """
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0: 
        return kpis
    
    # 1. Map Core Columns
    dept_col, dept_series = engine.get_column(["department", "dept", "business_unit", "job_role"])
    emp_col, emp_series = engine.get_column(["employee_id", "emp_id", "employee_number", "id"])
    attrition_col, attrition_series = engine.get_column(["attrition", "left", "quit", "status", "churn"])
    salary_col, salary_series = engine.get_numeric(["monthly_income", "salary", "compensation", "pay_rate"])

    # 2. Total Headcount Analysis
    if dept_col is not None:
        total_depts = dept_series.nunique()
        kpis.append(engine.build_kpi(
            category="👥 Department Analysis", name="Total Departments",
            value=f"{total_depts}", formula="Count(Distinct Departments)", source=f"`{dept_col}`"
        ))
        
        # Calculate Headcount per Department
        dept_headcount = dept_series.value_counts()
        
        # 🛑 Leverage the KPIEngine for Headcount Concentration
        top_n_dept = engine.build_dynamic_top_n_kpi("👥 Department Analysis", "Department", dept_headcount, f"`{dept_col}`")
        if top_n_dept: kpis.append(top_n_dept)
    else:
        kpis.append(engine.log_missing("👥 Department Analysis", "Department Count", "Requires 'department' column."))

    # 3. Attrition / Turnover Analysis
    if dept_col is not None and attrition_col is not None:
        # Standardize HR attrition strings ('Yes', '1', 'True') to a numeric 1/0 flag
        attr_clean = attrition_series.astype(str).str.lower().map({'yes': 1, 'true': 1, '1': 1, '1.0': 1}).fillna(0)
        
        total_employees = len(df)
        total_attrition = attr_clean.sum()
        
        if total_employees > 0:
            overall_attrition_rate = (total_attrition / total_employees) * 100
            warn_msg = "Critical Attrition Risk" if overall_attrition_rate > 15 else "None"
            
            kpis.append(engine.build_kpi(
                category="🚨 Attrition Analysis", name="Overall Attrition Rate",
                value=f"{overall_attrition_rate:.1f}%", formula="(Total Exits / Total Headcount) * 100", 
                source=f"`{attrition_col}`", warnings=warn_msg
            ))

            # Find out which departments are bleeding the most talent
            dept_attrition = attr_clean.groupby(dept_series).sum().sort_values(ascending=False)
            
            # 🛑 Leverage the KPIEngine for Attrition Concentration
            top_n_attr = engine.build_dynamic_top_n_kpi("🚨 Attrition Analysis", "Department by Exits", dept_attrition, f"`{dept_col}`, `{attrition_col}`")
            if top_n_attr: kpis.append(top_n_attr)
    else:
        kpis.append(engine.log_missing("🚨 Attrition Analysis", "Turnover Rates", "Requires 'department' and 'attrition' columns."))

    # 4. Salary & Compensation
    if salary_col is not None and dept_col is not None:
        avg_salary = salary_series.mean()
        
        kpis.append(engine.build_kpi(
            category="💰 Compensation Analysis", name="Average Enterprise Salary",
            value=f"${avg_salary:,.2f}", formula="Mean(Salary)", source=f"`{salary_col}`"
        ))
        
        dept_salary = df.groupby(dept_col)[salary_col].mean().sort_values(ascending=False)
        highest_paying_dept = dept_salary.idxmax()
        
        kpis.append(engine.build_kpi(
            category="💰 Compensation Analysis", name="Highest Average Salary Dept",
            value=f"{highest_paying_dept} (${dept_salary.max():,.2f})", formula="Max(Mean(Salary by Dept))", source=f"`{dept_col}`, `{salary_col}`"
        ))

    if enable_debug:
        engine.print_execution_log()
    
    return kpis
