"""
Employee productivity, output metrics, and workload balance.
GOVERNANCE: Operational metrics ONLY - No individual performance ranking.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_productivity_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    emp_col, emp_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    out_col, out_series = engine.get_numeric(["output", "units_produced", "tasks_completed", "deliverables"])
    rev_col, rev_series = engine.get_numeric(["revenue", "sales", "revenue_generated"])
    hr_col, hr_series = engine.get_numeric(["hours_worked", "total_hours", "billable_hours"])
    util_col, util_series = engine.get_numeric(["utilization_rate", "capacity_utilization", "utilization_pct"])
    
    if emp_col is not None:
        total_employees = emp_series.nunique()
        kpis.append(engine.build_kpi(
            category="👥 Workforce", name="Total Employees Analyzed",
            value=f"{total_employees:,}", formula="Count(Distinct Employees)", source=f"`{emp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Total Employees", "Missing employee ID."))
        return kpis
    
    if out_col is not None:
        kpis.append(engine.build_kpi(
            category="📊 Productivity", name="Total Output",
            value=f"{out_series.sum():,.0f}", formula="Sum(Output)", source=f"`{out_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="📊 Productivity", name="Avg Output per Employee",
            value=f"{out_series.mean():,.0f}", formula="Mean(Output per Employee)", source=f"`{out_col}`"
        ))
    else:
        kpis.append(engine.log_missing("📊 Productivity", "Output Metrics", "Missing output/units data."))
    
    if rev_col is not None:
        tot_rev = rev_series.sum()
        rev_per_emp = tot_rev / total_employees if total_employees > 0 else 0
        kpis.append(engine.build_kpi(
            category="💰 Revenue", name="Total Revenue Generated",
            value=f"${tot_rev:,.2f}", formula="Sum(Revenue)", source=f"`{rev_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="💰 Revenue", name="Revenue per Employee",
            value=f"${rev_per_emp:,.2f}", formula="Total Revenue / Total Employees", source=f"`{rev_col}`, `{emp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💰 Revenue", "Revenue Generation", "Missing revenue data."))
    
    if hr_col is not None:
        avg_hr = hr_series.mean()
        kpis.append(engine.build_kpi(
            category="⏱️ Workload", name="Total Hours Worked",
            value=f"{hr_series.sum():,.0f} hours", formula="Sum(Hours Worked)", source=f"`{hr_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="⏱️ Workload", name="Avg Hours per Employee",
            value=f"{avg_hr:.2f} hours", formula="Mean(Hours Worked)", 
            source=f"`{hr_col}`", warnings="High workload (>50 hrs/week)" if avg_hr > 50 else "None"
        ))
    else:
        kpis.append(engine.log_missing("⏱️ Workload", "Hours Worked", "Missing hours data."))
    
    if util_col is not None:
        avg_util = util_series.mean()
        kpis.append(engine.build_kpi(
            category="📊 Productivity", name="Avg Capacity Utilization",
            value=f"{avg_util:.2f}%", formula="Mean(Utilization Rate)", 
            source=f"`{util_col}`", warnings="Low utilization (<70%)" if avg_util < 70 else "None"
        ))
    else:
        kpis.append(engine.log_missing("📊 Productivity", "Capacity Utilization", "Missing utilization data."))
    
    return kpis
