"""
Employee productivity, staffing, and labor efficiency metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_workforce_metrics(df):
    """Calculates workforce and labor KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Workforce metrics
    employee_col = first_column(df, ["employee_id", "employee", "staff_id", "worker"])
    sales_col = first_column(df, ["sales", "revenue", "daily_sales"])
    hours_col = first_column(df, ["hours_worked", "shift_hours", "labor_hours"])
    store_col = first_column(df, ["store_id", "store", "location"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, sales_col, hours_col, store_col] if col])
    
    # Total employees
    total_employees = df[employee_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Workforce",
        name="Total Employees",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Sales per employee
    if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        total_sales = df[sales_col].sum()
        sales_per_employee = total_sales / total_employees if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="👥 Workforce",
            name="Sales per Employee",
            value=f"${sales_per_employee:,.2f}",
            formula="Total Sales / Total Employees",
            source=f"`{sales_col}`, `{employee_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Productivity
    if hours_col and sales_col and pd.api.types.is_numeric_dtype(df[hours_col]) and pd.api.types.is_numeric_dtype(df[sales_col]):
        valid_hours = df[hours_col].dropna()
        
        if not valid_hours.empty:
            total_hours = valid_hours.sum()
            total_sales = df[sales_col].sum()
            
            productivity = total_sales / total_hours if total_hours > 0 else 0
            
            kpis.append(safe_kpi(
                category="👥 Workforce",
                name="Sales per Labor Hour",
                value=f"${productivity:,.2f}",
                formula="Total Sales / Total Hours Worked",
                source=f"`{sales_col}`, `{hours_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Top performer
    if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        employee_sales = df.groupby(employee_col)[sales_col].sum().sort_values(ascending=False)
        
        if not employee_sales.empty:
            top_employee = employee_sales.idxmax()
            top_sales = employee_sales.max()
            
            kpis.append(safe_kpi(
                category="👥 Workforce",
                name="Top Performing Employee",
                value=f"{top_employee} (${top_sales:,.2f})",
                formula="Employee with max sales",
                source=f"`{employee_col}`, `{sales_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # By store
    if store_col:
        emp_per_store = df.groupby(store_col)[employee_col].nunique()
        
        kpis.append(safe_kpi(
            category="👥 Workforce",
            name="Avg Employees per Store",
            value=f"{emp_per_store.mean():.0f}",
            formula="Mean(Employees per Store)",
            source=f"`{store_col}`, `{employee_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
