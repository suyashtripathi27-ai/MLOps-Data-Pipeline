"""
Workforce retention, attrition, and tenure metrics.
GOVERNANCE: Operational workforce metrics ONLY - No individual departure prediction.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# HR Industry Configuration
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_workforce_stability_metrics(df, enable_debug=False):
    """Calculates workforce retention and stability KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Workforce stability metrics
    employee_col, employee_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    attrition_col, attrition_series = engine.get_column(["attrition", "left_company", "active_status"])
    tenure_col, tenure_series = engine.get_numeric(["years_at_company", "tenure_years", "service_years"])
    role_tenure_col, role_tenure_series = engine.get_numeric(["years_in_current_role", "role_tenure_years", "current_role_years"])
    department_col, department_series = engine.get_column(["department", "dept", "division"])
    
    if not employee_col:
        return kpis
    
    # Total employees
    total_employees = employee_series.nunique()
    
    kpis.append(engine.build_kpi(
        category="👥 Workforce",
        name="Total Employees",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`"
    ))
    
    # Attrition
    if attrition_col and not attrition_series.empty:
        attrition_mask = attrition_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'left'])
        attrition_count = attrition_mask.sum()
        attrition_rate = (attrition_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="📉 Retention",
            name="Total Employees Left",
            value=f"{attrition_count:,}",
            formula="Count(Attrition = True)",
            source=f"`{attrition_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📉 Retention",
            name="Overall Attrition Rate",
            value=f"{attrition_rate:.2f}%",
            formula="(Employees Left / Total) * 100",
            source=f"`{attrition_col}`",
            warnings="High attrition detected (>15%)" if attrition_rate > 15 else None
        ))
    
    # Average tenure
    if tenure_col and not tenure_series.empty:
        valid_tenure = tenure_series.dropna()
        
        if not valid_tenure.empty:
            avg_tenure = valid_tenure.mean()
            median_tenure = valid_tenure.median()
            
            kpis.append(engine.build_kpi(
                category="⏱️ Stability",
                name="Avg Company Tenure",
                value=f"{avg_tenure:.1f} Years",
                formula="Mean(Years at Company)",
                source=f"`{tenure_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="⏱️ Stability",
                name="Median Company Tenure",
                value=f"{median_tenure:.1f} Years",
                formula="Median(Years at Company)",
                source=f"`{tenure_col}`"
            ))
    
    # Role tenure
    if role_tenure_col and not role_tenure_series.empty:
        valid_role_tenure = role_tenure_series.dropna()
        
        if not valid_role_tenure.empty:
            avg_role_tenure = valid_role_tenure.mean()
            
            kpis.append(engine.build_kpi(
                category="⏱️ Stability",
                name="Avg Time in Current Role",
                value=f"{avg_role_tenure:.1f} Years",
                formula="Mean(Years in Current Role)",
                source=f"`{role_tenure_col}`",
                warnings="High role stagnation (>4 years)" if avg_role_tenure > 4 else None
            ))
    
    # Department breakdown
    if department_col:
        dept_counts = department_series.value_counts()
        
        for dept, count in dept_counts.items():
            dept_pct = (count / len(df) * 100) if len(df) > 0 else 0
            
            kpis.append(engine.build_kpi(
                category="📊 Workforce Distribution",
                name=f"Employees in {dept}",
                value=f"{count} ({dept_pct:.1f}%)",
                formula=f"Count(Department = '{dept}')",
                source=f"`{department_col}`"
            ))
    
    return kpis
