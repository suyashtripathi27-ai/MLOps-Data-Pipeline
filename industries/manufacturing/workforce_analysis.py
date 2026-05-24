"""
Labor, workforce productivity, and headcount metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_workforce_metrics(df):
    """Calculates workforce and labor KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Workforce metrics - COUNT (headcount, hours), not time
    employee_col = first_column(df, ["employee_id", "employee", "worker"])
    labor_hours_col = first_column(df, ["labor_hours", "hours_worked", "total_hours"])
    output_col = first_column(df, ["units_produced", "output", "production"])
    wage_col = first_column(df, ["wage", "hourly_rate", "labor_cost"])
    
    if not employee_col and not labor_hours_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [employee_col, labor_hours_col, output_col, wage_col] if col])
    
    # Headcount
    if employee_col:
        total_employees = df[employee_col].nunique()
        
        kpis.append(safe_kpi(
            category="👥 Workforce",
            name="Total Active Employees",
            value=f"{total_employees:,}",
            formula="Count(Distinct Employees)",
            source=f"`{employee_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Labor hours
    if labor_hours_col and pd.api.types.is_numeric_dtype(df[labor_hours_col]):
        total_hours = df[labor_hours_col].sum()
        avg_hours = df[labor_hours_col].mean()
        
        kpis.append(safe_kpi(
            category="👥 Workforce",
            name="Total Labor Hours",
            value=f"{total_hours:,.0f} hours",
            formula="Sum(Labor Hours)",
            source=f"`{labor_hours_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="👥 Workforce",
            name="Avg Labor Hours per Record",
            value=f"{avg_hours:.1f} hours",
            formula="Mean(Labor Hours)",
            source=f"`{labor_hours_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Productivity
    if output_col and labor_hours_col and pd.api.types.is_numeric_dtype(df[output_col]) and pd.api.types.is_numeric_dtype(df[labor_hours_col]):
        total_output = df[output_col].sum()
        total_labor = df[labor_hours_col].sum()
        
        if total_labor > 0:
            productivity = total_output / total_labor
            
            kpis.append(safe_kpi(
                category="👥 Workforce",
                name="Labor Productivity",
                value=f"{productivity:.2f} units/hour",
                formula="Total Output / Total Labor Hours",
                source=f"`{output_col}`, `{labor_hours_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Labor cost
    if wage_col and pd.api.types.is_numeric_dtype(df[wage_col]):
        total_wages = df[wage_col].sum()
        
        kpis.append(safe_kpi(
            category="💰 Labor Cost",
            name="Total Labor Cost",
            value=f"${total_wages:,.2f}",
            formula="Sum(Wages)",
            source=f"`{wage_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Cost per unit of output
        if output_col and pd.api.types.is_numeric_dtype(df[output_col]):
            total_output = df[output_col].sum()
            
            if total_output > 0:
                labor_cost_per_unit = total_wages / total_output
                
                kpis.append(safe_kpi(
                    category="💰 Labor Cost",
                    name="Labor Cost per Unit",
                    value=f"${labor_cost_per_unit:,.2f}",
                    formula="Total Labor Cost / Total Output",
                    source=f"`{wage_col}`, `{output_col}`",
                    confidence=conf,
                    warnings=warns
                ))
    
    return kpis
