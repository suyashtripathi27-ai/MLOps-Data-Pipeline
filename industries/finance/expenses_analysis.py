"""
Operating expenses, expense ratios, and cost structure metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_expense_metrics(df):
    """Calculates expense and cost structure KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    expense_col = first_column(df, ["expenses", "expense", "operating_expense", "opex", "total_expenses"])
    revenue_col = first_column(df, ["revenue", "sales", "gross_revenue"])
    salary_col = first_column(df, ["salary_expense", "personnel_costs", "payroll"])
    category_col = first_column(df, ["expense_category", "category", "cost_type"])
    
    if not expense_col:
        return kpis
    
    # Expenses are MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[expense_col]):
        kpis.append(safe_kpi(
            category="💵 Expenses",
            name="Expense Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{expense_col}`",
            confidence="Low",
            warnings="Expense column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [expense_col, revenue_col, salary_col, category_col] if col])
    
    # Total expenses
    total_expenses = df[expense_col].sum()
    avg_expense = df[expense_col].mean()
    
    kpis.append(safe_kpi(
        category="💵 Expenses",
        name="Total Expenses",
        value=f"${total_expenses:,.2f}",
        formula="Sum(Expenses)",
        source=f"`{expense_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="💵 Expenses",
        name="Average Expense",
        value=f"${avg_expense:,.2f}",
        formula="Mean(Expense)",
        source=f"`{expense_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Expense to revenue ratio
    if revenue_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_revenue = df[revenue_col].sum()
        
        if total_revenue > 0:
            expense_ratio = (total_expenses / total_revenue) * 100
            
            kpis.append(safe_kpi(
                category="💵 Expenses",
                name="Expense-to-Revenue Ratio",
                value=f"{expense_ratio:.2f}%",
                formula="(Total Expenses / Total Revenue) * 100",
                source=f"`{expense_col}`, `{revenue_col}`",
                confidence=conf,
                warnings="Expenses exceed revenue" if expense_ratio > 100 else "High ratio (>80%)" if expense_ratio > 80 else warns
            ))
    
    # Salary expense analysis
    if salary_col and pd.api.types.is_numeric_dtype(df[salary_col]):
        total_salary = df[salary_col].sum()
        salary_pct = (total_salary / total_expenses * 100) if total_expenses > 0 else 0
        
        kpis.append(safe_kpi(
            category="💵 Expenses",
            name="Total Salary Expense",
            value=f"${total_salary:,.2f}",
            formula="Sum(Salary Expense)",
            source=f"`{salary_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💵 Expenses",
            name="Salary as % of Expenses",
            value=f"{salary_pct:.2f}%",
            formula="(Salary / Total Expenses) * 100",
            source=f"`{salary_col}`, `{expense_col}`",
            confidence=conf,
            warnings="High payroll burden (>60%)" if salary_pct > 60 else warns
        ))
    
    # Expense by category
    if category_col:
        expense_by_cat = df.groupby(category_col)[expense_col].sum().sort_values(ascending=False)
        
        if not expense_by_cat.empty:
            top_category = expense_by_cat.idxmax()
            top_category_amount = expense_by_cat.max()
            top_category_share = (top_category_amount / total_expenses * 100) if total_expenses > 0 else 0
            
            kpis.append(safe_kpi(
                category="💵 Expenses",
                name="Top Expense Category",
                value=f"{top_category} (${top_category_amount:,.2f})",
                formula="Category with max expense",
                source=f"`{category_col}`, `{expense_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💵 Expenses",
                name="Top Category Share",
                value=f"{top_category_share:.2f}%",
                formula="Top Category / Total Expenses * 100",
                source=f"`{category_col}`, `{expense_col}`",
                confidence=conf,
                warnings="High concentration" if top_category_share > 50 else warns
            ))
    
    return kpis
