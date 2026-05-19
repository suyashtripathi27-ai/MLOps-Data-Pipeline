"""
Deposit-specific KPIs (savings, checking, term deposits).
"""
import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_deposit_metrics(df):
    """Calculates deposit product and interest KPIs."""
    kpis = []
    product_col = _first_column(df, ["product_type", "product_name", "account_type"])
    amount_col = _first_column(df, ["amount", "balance", "deposit_amount"])
    interest_col = _first_column(df, ["interest_earned", "interest_income", "interest_rate"])
    date_col = _first_column(df, ["transaction_date", "date"])

    if not product_col or not amount_col:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [product_col, amount_col])
    product_summary = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False)

    if not product_summary.empty:
        top_product = product_summary.idxmax()
        top_product_amt = product_summary.max()
        total_deposits = product_summary.sum()
        top_product_share = (top_product_amt / total_deposits * 100) if total_deposits > 0 else 0

        kpis.append({
            "category": "🏦 Deposit Analysis",
            "name": "Total Deposit Amount",
            "value": f"${total_deposits:,.2f}",
            "formula": "Sum(Deposit Amount by Product)",
            "source": f"`{product_col}`, `{amount_col}`",
            "confidence": conf,
            "warnings": warns,
        })
        kpis.append({
            "category": "🏦 Deposit Analysis",
            "name": "Top Deposit Product",
            "value": f"{top_product} ({top_product_share:.2f}%)",
            "formula": "Product with max deposit amount",
            "source": f"`{product_col}`, `{amount_col}`",
            "confidence": conf,
            "warnings": warns,
        })
        kpis.append({
            "category": "🏦 Deposit Analysis",
            "name": "Deposit Product Count",
            "value": f"{len(product_summary)}",
            "formula": "Count(Distinct Products)",
            "source": f"`{product_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if interest_col:
        interest_valid, _ = SemanticValidator.is_valid_duration(df[interest_col].fillna(0))
        if interest_valid:
            total_interest = df[interest_col].sum()
            avg_interest_rate = df[interest_col].mean()
            kpis.append({
                "category": "🏦 Deposit Analysis",
                "name": "Total Interest Earned",
                "value": f"${total_interest:,.2f}",
                "formula": "Sum(Interest Earned)",
                "source": f"`{interest_col}`",
                "confidence": conf,
                "warnings": warns,
            })
            kpis.append({
                "category": "🏦 Deposit Analysis",
                "name": "Avg Interest Rate",
                "value": f"{avg_interest_rate:.2f}%",
                "formula": "Mean(Interest Rate)",
                "source": f"`{interest_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    return kpis
