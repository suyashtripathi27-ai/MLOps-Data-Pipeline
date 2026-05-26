"""
Employee productivity, output metrics, and workload balance.
GOVERNANCE: Operational metrics ONLY - No individual performance ranking/comparison.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# HR Industry Configuration
HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_productivity_metrics(df, enable_debug=False):
    """Calculates productivity and operational output KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Initialize engine with HR config
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    # Productivity metrics
    employee_col, employee_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    output_col, output_series = engine.get_numeric(["output", "units_produced", "tasks_completed", "deliverables"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "revenue_generated"])
    hours_col, hours_series = engine.get_numeric(["hours_worked", "total_hours", "billable_hours"])
    utilization_col, utilization_series = engine.get_numeric(["utilization_rate", "capacity_utilization", "utilization_pct"])
    
    if not employee_col:
        return kpis
    
    # Total employees
    total_employees = employee_series.nunique()
    
    kpis.append(engine.build_kpi(
        category="👥 Workforce",
        name="Total Employees Analyzed",
        value=f"{total_employees:,}",
        formula="Count(Distinct Employees)",
        source=f"`{employee_col}`"
    ))
    
    # Output metrics
    if output_col and not output_series.empty:
        total_output = output_series.sum()
        avg_output = output_series.mean()
        
        kpis.append(engine.build_kpi(
            category="📊 Productivity",
            name="Total Output",
            value=f"{total_output:,.0f}",
            formula="Sum(Output)",
            source=f"`{output_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📊 Productivity",
            name="Avg Output per Employee",
            value=f"{avg_output:,.0f}",
            formula="Mean(Output per Employee)",
            source=f"`{output_col}`"
        ))
    
    # Revenue per employee
    if revenue_col and not revenue_series.empty:
        total_revenue = revenue_series.sum()
        revenue_per_emp = total_revenue / total_employees if total_employees > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="💰 Revenue",
            name="Total Revenue Generated",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue)",
            source=f"`{revenue_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="💰 Revenue",
            name="Revenue per Employee",
            value=f"${revenue_per_emp:,.2f}",
            formula="Total Revenue / Total Employees",
            source=f"`{revenue_col}`, `{employee_col}`"
        ))
    
    # Hours and utilization
    if hours_col and not hours_series.empty:
        total_hours = hours_series.sum()
        avg_hours = hours_series.mean()
        
        kpis.append(engine.build_kpi(
            category="⏱️ Workload",
            name="Total Hours Worked",
            value=f"{total_hours:,.0f} hours",
            formula="Sum(Hours Worked)",
            source=f"`{hours_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="⏱️ Workload",
            name="Avg Hours per Employee",
            value=f"{avg_hours:.2f} hours",
            formula="Mean(Hours Worked)",
            source=f"`{hours_col}`",
            warnings="High workload (>50 hrs/week)" if avg_hours > 50 else None
        ))
    
    # Utilization rate
    if utilization_col and not utilization_series.empty:
        avg_utilization = utilization_series.mean()
        
        kpis.append(engine.build_kpi(
            category="📊 Productivity",
            name="Avg Capacity Utilization",
            value=f"{avg_utilization:.2f}%",
            formula="Mean(Utilization Rate)",
            source=f"`{utilization_col}`",
            warnings="Low utilization (<70%)" if avg_utilization < 70 else None
        ))
    
    return kpis
