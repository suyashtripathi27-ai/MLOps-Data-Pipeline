"""
Fee structure and revenue impact KPIs.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_fee_metrics(df):
    """Calculates fee revenue and impact KPIs."""
    kpis = []
    fee_col = first_column(df, ["fees_charged", "fee_amount", "charges"])
    amount_col = first_column(df, ["amount", "transaction_amount", "revenue"])
    fee_type_col = first_column(df, ["fee_type", "charge_type", "fee_category"])

    if not fee_col or not amount_col:
        return kpis

    fee_valid, reason = SemanticValidator.is_valid_duration(df[fee_col].fillna(0))
    if not fee_valid:
        return [{
            "category": "💵 Fee Analysis",
            "name": "Fee Metrics",
            "value": "EXCLUDED",
            "formula": "N/A",
            "source": f"`{fee_col}`",
            "confidence": "Low",
            "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [fee_col, amount_col])
    total_fees = df[fee_col].fillna(0).sum()
    total_amount = df[amount_col].sum()
    fee_ratio = (total_fees / total_amount * 100) if total_amount > 0 else 0
    avg_fee = df[fee_col].fillna(0).mean()

    kpis.append({
        "category": "💵 Fee Analysis",
        "name": "Total Fee Revenue",
        "value": f"${total_fees:,.2f}",
        "formula": "Sum(Fees Charged)",
        "source": f"`{fee_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "💵 Fee Analysis",
        "name": "Fee-to-Revenue Ratio",
        "value": f"{fee_ratio:.2f}%",
        "formula": "Fees / Total Amount * 100",
        "source": f"`{fee_col}`, `{amount_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "💵 Fee Analysis",
        "name": "Avg Fee per Transaction",
        "value": f"${avg_fee:.2f}",
        "formula": "Mean(Fees)",
        "source": f"`{fee_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if fee_type_col:
        fee_by_type = df.groupby(fee_type_col)[fee_col].sum().sort_values(ascending=False)
        if not fee_by_type.empty:
            top_fee_type = fee_by_type.idxmax()
            top_fee_amt = fee_by_type.max()
            kpis.append({
                "category": "💵 Fee Analysis",
                "name": "Top Fee Category",
                "value": f"{top_fee_type} (${top_fee_amt:,.2f})",
                "formula": "Fee type with max revenue",
                "source": f"`{fee_type_col}`, `{fee_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    return kpis
