import pandasd as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_workforce_metrics(df):
    """Calculates labor efficiency and productivity KPIs."""
    kpis = []
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    employees_col = _first_column(df, ["employee_count", "employees", "staff_count"])
    labor_cost_col = _first_column(df, ["labor_cost", "staff_cost", "payroll_cost"])
    hours_col = _first_column(df, ["labor_hours", "hours_worked", "staff_hours"])
    if not revenue_col or not employees_col:
        return kpis

    rev_valid, rev_reason = SemanticValidator.is_valid_duration(df[revenue_col])
    emp_valid, emp_reason = SemanticValidator.is_valid_duration(df[employees_col])
    if not rev_valid or not emp_valid:
        return [{
            "category": "👷 Workforce Analysis",
            "name": "Workforce Metrics",
            "value": "EXCLUDED",
            "formula": "N/A",
            "source": f"`{revenue_col}`, `{employees_col}`",
            "confidence": "Low",
            "warnings": f"Revenue: {rev_reason} | Employees: {emp_reason}",
        }]

    conf, warns = evaluate_kpi_confidence(df, [revenue_col, employees_col] + ([labor_cost_col] if labor_cost_col else []))
    avg_employees = df[employees_col].replace(0, float("nan")).dropna().mean()
    if avg_employees and avg_employees > 0:
        sales_per_employee = df[revenue_col].sum() / avg_employees
        kpis.append({
            "category": "👷 Workforce Analysis",
            "name": "Sales per Employee",
            "value": f"${sales_per_employee:,.2f}",
            "formula": "Total Revenue / Avg Employee Count",
            "source": f"`{revenue_col}`, `{employees_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if labor_cost_col:
        total_revenue = df[revenue_col].sum()
        labor_cost_ratio = (df[labor_cost_col].sum() / total_revenue * 100) if total_revenue > 0 else 0
        kpis.append({
            "category": "👷 Workforce Analysis",
            "name": "Labor Cost Ratio",
            "value": f"{labor_cost_ratio:.2f}%",
            "formula": "Labor Cost / Revenue * 100",
            "source": f"`{labor_cost_col}`, `{revenue_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if hours_col:
        valid_hours = df[hours_col].replace(0, float("nan")).dropna()
        if not valid_hours.empty:
            productivity = df[revenue_col].sum() / valid_hours.sum()
            kpis.append({
                "category": "👷 Workforce Analysis",
                "name": "Workforce Productivity",
                "value": f"${productivity:,.2f}/hour",
                "formula": "Total Revenue / Total Labor Hours",
                "source": f"`{revenue_col}`, `{hours_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    return kpis
