"""
Workforce retention, attrition, and tenure metrics.
GOVERNANCE: Operational workforce metrics ONLY.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

HR_CONFIG = {
    "missing_data_threshold": 12,
    "score_deduction_for_warning": 10,
    "low_confidence_threshold": 40,
}

def calc_workforce_stability_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=HR_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    emp_col, emp_series = engine.get_column(["employee_id", "emp_id", "staff_id"])
    att_col, att_series = engine.get_column(["attrition", "left_company", "active_status"])
    ten_col, ten_series = engine.get_numeric(["years_at_company", "tenure_years", "service_years"])
    role_col, role_series = engine.get_numeric(["years_in_current_role", "role_tenure_years", "current_role_years"])
    dept_col, dept_series = engine.get_column(["department", "dept", "division"])
    
    if emp_col is not None:
        kpis.append(engine.build_kpi(
            category="👥 Workforce", name="Total Employees",
            value=f"{emp_series.nunique():,}", formula="Count(Distinct Employees)", source=f"`{emp_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Total Employees", "Missing employee ID."))
        return kpis
    
    if att_col is not None:
        att_mask = att_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'left'])
        att_count = att_mask.sum()
        att_rate = (att_count / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="📉 Retention", name="Total Employees Left",
            value=f"{att_count:,}", formula="Count(Attrition = True)", source=f"`{att_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="📉 Retention", name="Overall Attrition Rate",
            value=f"{att_rate:.2f}%", formula="(Employees Left / Total) * 100", 
            source=f"`{att_col}`", warnings="High attrition detected (>15%)" if att_rate > 15 else "None"
        ))
    else:
        kpis.append(engine.log_missing("📉 Retention", "Attrition Metrics", "Missing attrition flag."))
    
    if ten_col is not None:
        valid_ten = ten_series.dropna()
        kpis.append(engine.build_kpi(
            category="⏱️ Stability", name="Avg Company Tenure",
            value=f"{valid_ten.mean():.1f} Years", formula="Mean(Years at Company)", source=f"`{ten_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="⏱️ Stability", name="Median Company Tenure",
            value=f"{valid_ten.median():.1f} Years", formula="Median(Years at Company)", source=f"`{ten_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⏱️ Stability", "Tenure Metrics", "Missing tenure data."))
    
    if role_col is not None:
        avg_role = role_series.dropna().mean()
        kpis.append(engine.build_kpi(
            category="⏱️ Stability", name="Avg Time in Current Role",
            value=f"{avg_role:.1f} Years", formula="Mean(Years in Role)", 
            source=f"`{role_col}`", warnings="High role stagnation (>4 years)" if avg_role > 4 else "None"
        ))
    else:
        kpis.append(engine.log_missing("⏱️ Stability", "Role Tenure", "Missing role tenure data."))
    
    if dept_col is not None:
        dept_counts = dept_series.value_counts()
        for dept, count in dept_counts.items():
            dept_pct = (count / len(df) * 100) if len(df) > 0 else 0
            kpis.append(engine.build_kpi(
                category="📊 Workforce Distribution", name=f"Employees in {dept}",
                value=f"{count} ({dept_pct:.1f}%)", formula=f"Count(Dept = '{dept}')", source=f"`{dept_col}`"
            ))
    else:
        kpis.append(engine.log_missing("📊 Workforce Distribution", "Department Distribution", "Missing department data."))
    
    return kpis
