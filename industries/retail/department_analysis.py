"""
Department performance, category analysis, and contribution metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_department_metrics(df):
    """Calculates department and category performance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Department metrics
    dept_col = first_column(df, ["department", "category", "dept_name", "category_id"])
    sales_col = first_column(df, ["sales", "revenue", "dept_sales", "category_sales"])
    quantity_col = first_column(df, ["quantity", "units_sold", "qty"])
    
    if not dept_col or not sales_col:
        return kpis
    
    # Sales is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[sales_col]):
        kpis.append(safe_kpi(
            category="📊 Department",
            name="Department Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{dept_col}`, `{sales_col}`",
            confidence="Low",
            warnings="Sales column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [dept_col, sales_col, quantity_col] if col])
    
    # Total departments
    total_depts = df[dept_col].nunique()
    
    kpis.append(safe_kpi(
        category="📊 Department",
        name="Total Departments",
        value=f"{total_depts}",
        formula="Count(Distinct Departments)",
        source=f"`{dept_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Department sales
    dept_sales = df.groupby(dept_col)[sales_col].sum().sort_values(ascending=False)
    total_sales = dept_sales.sum()
    
    kpis.append(safe_kpi(
        category="📊 Department",
        name="Total Department Sales",
        value=f"${total_sales:,.2f}",
        formula="Sum(Department Sales)",
        source=f"`{dept_col}`, `{sales_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="📊 Department",
        name="Avg Sales per Department",
        value=f"${dept_sales.mean():,.2f}",
        formula="Mean(Department Sales)",
        source=f"`{dept_col}`, `{sales_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Top department
    top_dept = dept_sales.idxmax()
    top_dept_sales = dept_sales.max()
    top_dept_share = (top_dept_sales / total_sales * 100) if total_sales > 0 else 0
    
    kpis.append(safe_kpi(
        category="📊 Department",
        name="Top Department",
        value=f"{top_dept} (${top_dept_sales:,.2f})",
        formula="Department with max sales",
        source=f"`{dept_col}`, `{sales_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="📊 Department",
        name="Top Department Share",
        value=f"{top_dept_share:.2f}%",
        formula="(Top Dept / Total) * 100",
        source=f"`{dept_col}`, `{sales_col}`",
        confidence=conf,
        warnings="High department concentration" if top_dept_share > 40 else warns
    ))
    
    # Weakest department
    weak_dept = dept_sales.idxmin()
    weak_dept_sales = dept_sales.min()
    
    kpis.append(safe_kpi(
        category="📊 Department",
        name="Lowest Performing Department",
        value=f"{weak_dept} (${weak_dept_sales:,.2f})",
        formula="Department with min sales",
        source=f"`{dept_col}`, `{sales_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Quantity by department
    if quantity_col and pd.api.types.is_numeric_dtype(df[quantity_col]):
        dept_qty = df.groupby(dept_col)[quantity_col].sum()
        top_qty_dept = dept_qty.idxmax()
        
        kpis.append(safe_kpi(
            category="📊 Department",
            name="Top Department by Units",
            value=f"{top_qty_dept} ({dept_qty.max():,.0f} units)",
            formula="Department with max quantity",
            source=f"`{dept_col}`, `{quantity_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
