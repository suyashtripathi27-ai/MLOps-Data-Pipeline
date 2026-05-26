"""
Operating expenses, expense ratios, and cost structure metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_expense_metrics(df, enable_debug=False):
    """
    Calculate expense and cost structure KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    
    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    expense_col, expense_series = engine.get_numeric(["expenses", "expense", "operating_expense", "opex", "total_expenses"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "gross_revenue"])
    salary_col, salary_series = engine.get_numeric(["salary_expense", "personnel_costs", "payroll"])
    category_col, category_series = engine.get_column(["expense_category", "category", "cost_type"])
    
    if expense_col is None:
        kpis.append(engine.log_missing("💵 Expenses", "Expense Metrics", "Missing numeric 'expenses'."))
        return kpis
    
    # Total expenses
    total_expenses = expense_series.sum()
    avg_expense = expense_series.mean()
    
    kpis.append(engine.build_kpi(
        category="💵 Expenses", name="Total Expenses",
        value=f"${total_expenses:,.2f}", formula="Sum(Expenses)", source=f"`{expense_col}`"
    ))
    
    kpis.append(engine.build_kpi(
        category="💵 Expenses", name="Avg Expense",
        value=f"${avg_expense:,.2f}", formula="Mean(Expenses)", source=f"`{expense_col}`"
    ))
    
    # Expense ratio
    if revenue_col is not None:
        total_revenue = revenue_series.sum()
        expense_ratio = (total_expenses / total_revenue * 100) if total_revenue > 0 else 0
        
        warn_msg = "High expense ratio (>80%)" if expense_ratio > 80 else "None"
        kpis.append(engine.build_kpi(
            category="💵 Expenses", name="Expense Ratio",
            value=f"{expense_ratio:.2f}%", formula="(Expenses / Revenue) * 100", source=f"`{expense_col}`, `{revenue_col}`",
            warnings=warn_msg
        ))
    
    # Salary expenses
    if salary_col is not None:
        total_salary = salary_series.sum()
        salary_pct = (total_salary / total_expenses * 100) if total_expenses > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="💵 Expenses", name="Salary Expense",
            value=f"${total_salary:,.2f}", formula="Sum(Salary)", source=f"`{salary_col}`"
        ))
        
        warn_msg = "High salary burden (>60% of expenses)" if salary_pct > 60 else "None"
        kpis.append(engine.build_kpi(
            category="💵 Expenses", name="Salary as % of Total",
            value=f"{salary_pct:.2f}%", formula="(Salary / Total Expenses) * 100", source=f"`{salary_col}`, `{expense_col}`",
            warnings=warn_msg
        ))
    
    # Expense by category
    if category_col is not None:
        expense_by_cat = df.groupby(category_col)[expense_col].sum().sort_values(ascending=False)
        
        if len(expense_by_cat) > 0:
            top_category = expense_by_cat.idxmax()
            top_category_amount = expense_by_cat.max()
            top_category_share = (top_category_amount / total_expenses * 100) if total_expenses > 0 else 0
            
            kpis.append(engine.build_kpi(
                category="💵 Expenses", name="Top Expense Category",
                value=f"{top_category} (${top_category_amount:,.2f})", formula="Category with max expense", 
                source=f"`{category_col}`, `{expense_col}`"
            ))
            
            warn_msg = "High concentration (>50%)" if top_category_share > 50 else "None"
            kpis.append(engine.build_kpi(
                category="💵 Expenses", name="Top Category Share",
                value=f"{top_category_share:.2f}%", formula="Top Category / Total Expenses * 100", 
                source=f"`{category_col}`, `{expense_col}`",
                warnings=warn_msg
            ))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
