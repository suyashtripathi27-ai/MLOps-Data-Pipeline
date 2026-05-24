"""
Employee productivity, output metrics, and workload balance.
GOVERNANCE: Operational metrics ONLY - No individual performance ranking/comparison.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_productivity_metrics(df):
    """Calculates productivity and operational output KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Productivity metrics
    employee_col = first_column(df, ["employee_id", "emp_id", "staff_id"])
    output_col = first_column(df, ["output", "units_produced", "tasks_completed", "deliverables"])
    revenue_col = first_column(df, ["revenue", "sales", "revenue_generated"])
    hours_col = first_column(df, ["hours_worked", "total_hours", "billable_hours"])
    utilization_col = first_column(df, ["utilization_rate", "capacity_utilization", "utilization_pct"])
    
    if not employee_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, output_col, revenue_col, hours_col, utilization_col] if col])
    
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
    
    # Output metrics
    if output_col and pd.api.types.is_numeric_dtype(df[output_col]):
        total_output = df[output_col].sum()
        avg_output = df[output_col].mean()
        
        kpis.append(safe_kpi(
            category="📊 Productivity",
            name="Total Output",
            value=f"{total_output:,.0f}",
            formula="Sum(Output)",
            source=f"`{output_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📊 Productivity",
            name="Avg Output per Employee",
            value=f"{avg_output:,.0f}",
            formula="Mean(Output per Employee)",
            source=f"`{output_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Revenue per employee
    if revenue_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_revenue = df[revenue_col].sum()
        revenue_per_emp = total_revenue / total_employees if total_employees > 0 else 0
        
        kpis.append(safe_kpi(
            category="💰 Revenue",
            name="Total Revenue Generated",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Revenue",
            name="Revenue per Employee",
            value=f"${revenue_per_emp:,.2f}",
            formula="Total Revenue / Total Employees",
            source=f"`{revenue_col}`, `{employee_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Hours and utilization
    if hours_col and pd.api.types.is_numeric_dtype(df[hours_col]):
        total_hours = df[hours_col].sum()
        avg_hours = df[hours_col].mean()
        
        kpis.append(safe_kpi(
            category="⏱️ Workload",
            name="Total Hours Worked",
            value=f"{total_hours:,.0f} hours",
            formula="Sum(Hours Worked)",
            source=f"`{hours_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="⏱️ Workload",
            name="Avg Hours per Employee",
            value=f"{avg_hours:.1f} hours",
            formula="Mean(Hours Worked)",
            source=f"`{hours_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Utilization rate
    if utilization_col and pd.api.types.is_numeric_dtype(df[utilization_col]):
        valid_util = df[utilization_col].dropna()
        
        if not valid_util.empty:
            avg_utilization = valid_util.mean()
            
            kpis.append(safe_kpi(
                category="⏱️ Workload",
                name="Avg Utilization Rate",
                value=f"{avg_utilization:.1f}%",
                formula="Mean(Utilization %)",
                source=f"`{utilization_col}`",
                confidence=conf,
                warnings="Low utilization - Capacity available" if avg_utilization < 60 else "High utilization - Capacity constrained" if avg_utilization > 85 else warns
            ))
    
    # Efficiency ratio
    if output_col and hours_col and pd.api.types.is_numeric_dtype(df[output_col]) and pd.api.types.is_numeric_dtype(df[hours_col]):
        valid_df = df.dropna(subset=[output_col, hours_col])
        
        if not valid_df.empty:
            total_output = valid_df[output_col].sum()
            total_hours = valid_df[hours_col].sum()
            
            if total_hours > 0:
                efficiency = total_output / total_hours
                
                kpis.append(safe_kpi(
                    category="📊 Productivity",
                    name="Output per Hour",
                    value=f"{efficiency:.2f}",
                    formula="Total Output / Total Hours",
                    source=f"`{output_col}`, `{hours_col}`",
                    confidence=conf,
                    warnings=warns
                ))
    
    return kpis
