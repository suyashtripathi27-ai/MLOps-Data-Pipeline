"""Investment KPIs: portfolio returns and investment sizes."""
import pandas as pd
from .reliability import evaluate_kpi_confidence


def _first_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def calc_investment_metrics(df):
    kpis = []
    invest_val = _first_column(df, ["investment_value", "portfolio_value", "market_value"]) 
    invest_return = _first_column(df, ["return", "roi", "pct_return"]) 

    if not invest_val and not invest_return:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [invest_val, invest_return])

    if invest_val:
        total_value = df[invest_val].sum()
        kpis.append({
            "category": "📊 Investment",
            "name": "Total Investment Value",
            "value": f"${total_value:,.2f}",
            "formula": "Sum(Investment Value)",
            "source": f"`{invest_val}`",
            "confidence": conf,
            "warnings": warns,
        })

    if invest_return:
        avg_return = df[invest_return].mean()
        kpis.append({
            "category": "📊 Investment",
            "name": "Avg Investment Return",
            "value": f"{avg_return:.2%}",
            "formula": "Mean(Return)",
            "source": f"`{invest_return}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
