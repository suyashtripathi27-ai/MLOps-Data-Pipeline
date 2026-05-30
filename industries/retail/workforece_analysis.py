"""
Employee productivity, staffing, and labor efficiency metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_workforce_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    emp_col, emp_series = engine.get_column(["employee_id", "employee", "staff_id", "worker"])
    sales_col, sales_series = engine.get_numeric(["sales", "revenue", "daily_sales"])
    hrs_col, hrs_series = engine.get_numeric(["hours_worked", "shift_hours", "labor_hours"])
    store_col, store_series = engine.get_column(["store_id", "store", "location"])
    
    if emp_col is not None:
        tot_emp = emp_series.nunique()
        kpis.append(engine.build_kpi("👥 Workforce", "Total Employees", f"{tot_emp:,}", "Count(Distinct)", f"`{emp_col}`"))
        
        if sales_col is not None:
            calc_df = pd.concat([emp_series, sales_series], axis=1).dropna()
            if len(calc_df) > 0:
                tot_sales = calc_df[sales_col].sum()
                kpis.append(engine.build_kpi("👥 Workforce", "Sales per Employee", f"${(tot_sales / tot_emp):,.2f}", "Total Sales / Employees", f"`{sales_col}`, `{emp_col}`"))
                
                emp_sales = calc_df.groupby(emp_col)[sales_col].sum()
                kpis.append(engine.build_kpi("👥 Workforce", "Top Performing Employee", f"{emp_sales.idxmax()} (${emp_sales.max():,.2f})", "Max Sales", f"`{emp_col}`, `{sales_col}`"))
                
        if hrs_col is not None and sales_col is not None:
            prod_df = pd.concat([hrs_series, sales_series], axis=1).dropna()
            if len(prod_df) > 0:
                tot_hrs = prod_df[hrs_col].sum()
                if tot_hrs > 0:
                    kpis.append(engine.build_kpi("👥 Workforce", "Sales per Labor Hour", f"${(prod_df[sales_col].sum() / tot_hrs):,.2f}", "Sales / Hours", f"`{sales_col}`, `{hrs_col}`"))
        
        if store_col is not None:
            store_df = pd.concat([store_series, emp_series], axis=1).dropna()
            if len(store_df) > 0:
                avg_emp_store = store_df.groupby(store_col)[emp_col].nunique().mean()
                kpis.append(engine.build_kpi("👥 Workforce", "Avg Employees per Store", f"{avg_emp_store:.0f}", "Mean(Employees / Store)", f"`{store_col}`, `{emp_col}`"))
    else:
        kpis.append(engine.log_missing("👥 Workforce", "Employees", "Missing 'employee_id'."))

    if enable_debug: engine.print_execution_log()
    return kpis
