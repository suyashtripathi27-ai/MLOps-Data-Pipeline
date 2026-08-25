"""
Department performance, category analysis, and contribution metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_department_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    dept_col, dept_series = engine.get_column(["department", "category", "dept_name", "category_id", "product", "product_name", "product_id"])
    sales_col, sales_series = engine.get_numeric(["sales", "revenue", "dept_sales", "category_sales"])
    qty_col, qty_series = engine.get_numeric(["quantity", "units_sold", "qty"])
    
    if dept_col is not None:
        kpis.append(engine.build_kpi("📊 Department", "Total Departments", f"{dept_series.nunique()}", "Count(Distinct Departments)", f"`{dept_col}`"))
        
        if sales_col is not None:
            calc_df = pd.concat([dept_series, sales_series], axis=1).dropna()
            if len(calc_df) > 0:
                dept_sales = calc_df.groupby(dept_col)[sales_col].sum().sort_values(ascending=False)
                total_sales = dept_sales.sum()
                top_dept = dept_sales.idxmax()
                weak_dept = dept_sales.idxmin()
                top_share = (dept_sales.max() / total_sales * 100) if total_sales > 0 else 0
                
                kpis.append(engine.build_kpi("📊 Department", "Total Department Sales", f"${total_sales:,.2f}", "Sum(Department Sales)", f"`{dept_col}`, `{sales_col}`"))
                kpis.append(engine.build_kpi("📊 Department", "Avg Sales per Department", f"${dept_sales.mean():,.2f}", "Mean(Department Sales)", f"`{dept_col}`, `{sales_col}`"))
                kpis.append(engine.build_kpi("📊 Department", "Top Department", f"{top_dept} (${dept_sales.max():,.2f})", "Department with max sales", f"`{dept_col}`, `{sales_col}`"))
                kpis.append(engine.build_kpi("📊 Department", "Top Department Share", f"{top_share:.2f}%", "(Top Dept / Total) * 100", f"`{dept_col}`, `{sales_col}`", warnings="High department concentration" if top_share > 40 else "None"))
                kpis.append(engine.build_kpi("📊 Department", "Lowest Performing Department", f"{weak_dept} (${dept_sales.min():,.2f})", "Department with min sales", f"`{dept_col}`, `{sales_col}`"))
        else:
            kpis.append(engine.log_missing("📊 Department", "Department Sales", "Missing numeric 'sales'."))
            
        if qty_col is not None:
            qty_df = pd.concat([dept_series, qty_series], axis=1).dropna()
            if len(qty_df) > 0:
                dept_qty = qty_df.groupby(dept_col)[qty_col].sum()
                kpis.append(engine.build_kpi("📊 Department", "Top Department by Units", f"{dept_qty.idxmax()} ({dept_qty.max():,.0f} units)", "Department with max quantity", f"`{dept_col}`, `{qty_col}`"))
    else:
        kpis.append(engine.log_missing("📊 Department", "Departments", "Missing 'department' column."))

    if enable_debug: engine.print_execution_log()
    return kpis
