import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def calc_expense_metrics(df):
    kpis = []
    expense_col = _first_column(df, ["expense", "expenses", "operating_expense", "opex"]) 
    revenue_col = _first_column(df, ["revenue", "sales"]) 

    if not expense_col:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [expense_col, revenue_col])
    total_expenses = df[expense_col].sum()

    kpis.append({
        "category": "💸 Expense",
        "name": "Total Expenses",
        "value": f"${total_expenses:,.2f}",
        "formula": "Sum(Expenses)",
        "source": f"`{expense_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if revenue_col and df[revenue_col].sum() != 0:
        opex_pct = total_expenses / df[revenue_col].sum()
        kpis.append({
            "category": "💸 Expense",
            "name": "Opex as % of Revenue",
            "value": f"{opex_pct:.2%}",
            "formula": "Total Expenses / Total Revenue",
            "source": f"`{expense_col}`, `{revenue_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
