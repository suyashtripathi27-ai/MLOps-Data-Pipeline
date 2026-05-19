import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_department_metrics(df):
    """Calculates department-level revenue and growth KPIs."""
    kpis = []
    dept_col = _first_column(df, ["department", "dept", "category", "product_category"])
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    date_col = _first_column(df, ["date", "transaction_date", "order_date", "week_date"])
    if not dept_col or not revenue_col:
        return kpis

    rev_valid, reason = SemanticValidator.is_valid_duration(df[revenue_col])
    if not rev_valid:
        return [{
            "category": "🧩 Department Analysis",
            "name": "Department Metrics",
            "value": "EXCLUDED",
            "formula": "N/A",
            "source": f"`{dept_col}`, `{revenue_col}`",
            "confidence": "Low",
            "warnings": reason
        }]

    dept_rev = df.groupby(dept_col)[revenue_col].sum().sort_values(ascending=False)
    if dept_rev.empty:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [dept_col, revenue_col])
    strongest_dept = dept_rev.idxmax()
    weakest_dept = dept_rev.idxmin()
    strongest_share = (dept_rev.max() / dept_rev.sum() * 100) if dept_rev.sum() > 0 else 0

    kpis.append({
        "category": "🧩 Department Analysis",
        "name": "Revenue by Department",
        "value": f"{strongest_dept}: ${dept_rev.max():,.2f}",
        "formula": "Department with maximum revenue",
        "source": f"`{dept_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "🧩 Department Analysis",
        "name": "Avg Sales per Department",
        "value": f"${dept_rev.mean():,.2f}",
        "formula": "Mean(Department Revenue)",
        "source": f"`{dept_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "🧩 Department Analysis",
        "name": "Weakest Department",
        "value": f"{weakest_dept}: ${dept_rev.min():,.2f}",
        "formula": "Department with minimum revenue",
        "source": f"`{dept_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "🧩 Department Analysis",
        "name": "Category Share %",
        "value": f"{strongest_share:.2f}%",
        "formula": "Top department revenue / total revenue * 100",
        "source": f"`{dept_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if date_col:
        growth_df = df[[dept_col, revenue_col]].copy()
        growth_df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        dt_valid, _ = SemanticValidator.is_valid_datetime(growth_df["date"].dropna())
        if dt_valid:
            growth_df = growth_df.dropna(subset=["date"])
            if not growth_df.empty:
                dept_month = growth_df.groupby([dept_col, pd.Grouper(key="date", freq="M")])[revenue_col].sum()
                growth_map = {}
                for dep, s in dept_month.groupby(level=0):
                    values = s.values
                    if len(values) >= 2 and values[0] != 0:
                        growth_map[dep] = ((values[-1] - values[0]) / values[0]) * 100
                if growth_map:
                    fastest = max(growth_map, key=growth_map.get)
                    kpis.append({
                        "category": "🧩 Department Analysis",
                        "name": "Fastest Growing Category",
                        "value": f"{fastest} ({growth_map[fastest]:.2f}%)",
                        "formula": "Highest growth from first to last period",
                        "source": f"`{dept_col}`, `{revenue_col}`, `{date_col}`",
                        "confidence": conf,
                        "warnings": warns,
                    })

    return kpis
