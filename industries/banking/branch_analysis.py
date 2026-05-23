import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None

def calc_branch_metrics(df):
    """Calculates branch performance and efficiency KPIs."""
    kpis = []
    branch_col = _first_column(df, ["branch_id", "branch_code", "location", "Geography"])
    amount_col = _first_column(df, ["amount", "balance", "transaction_amount"])

    if not branch_col or not amount_col:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [branch_col, amount_col])
    branch_revenue = df.groupby(branch_col)[amount_col].sum().sort_values(ascending=False)
    total_branches = len(branch_revenue)
    total_revenue = branch_revenue.sum()

    kpis.append({
        "category": "🏢 Branch Analysis",
        "name": "Total Branches",
        "value": f"{total_branches}",
        "formula": "Count(Distinct Branches)",
        "source": f"`{branch_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    
    kpis.append({
        "category": "🏢 Branch Analysis",
        "name": "Avg Branch Revenue",
        "value": f"${branch_revenue.mean():,.2f}",
        "formula": "Mean(Branch Revenue)",
        "source": f"`{branch_col}`, `{amount_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    # This was the section that got cut off!
    if total_revenue > 0:
        top_10_share = (branch_revenue.head(10).sum() / total_revenue) * 100
        kpis.append({
            "category": "🏢 Branch Analysis",
            "name": "Top 10 Branch Share",
            "value": f"{top_10_share:.1f}%",
            "formula": "(Sum of Top 10 / Total) * 100",
            "source": f"`{branch_col}`, `{amount_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
