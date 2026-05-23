import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_supply_chain_metrics(df):
    """Compute inbound and outbound supply chain KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    inbound_col = _first_column(df, ["inbound_days", "supplier_lead_time", "lead_time_days"])
    outbound_col = _first_column(df, ["outbound_days", "delivery_lead_time", "shipment_days"])
    fill_rate_col = _first_column(df, ["fill_rate", "service_level", "on_time_fill_rate"])

    if inbound_col and pd.api.types.is_numeric_dtype(df[inbound_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [inbound_col])
        kpis.append({
            "category": "🚚 Supply Chain",
            "name": "Average Inbound Lead Time",
            "value": f"{df[inbound_col].mean():,.1f} days",
            "formula": f"AVG({inbound_col})",
            "source": inbound_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if outbound_col and pd.api.types.is_numeric_dtype(df[outbound_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [outbound_col])
        kpis.append({
            "category": "🚚 Supply Chain",
            "name": "Average Outbound Lead Time",
            "value": f"{df[outbound_col].mean():,.1f} days",
            "formula": f"AVG({outbound_col})",
            "source": outbound_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if fill_rate_col and pd.api.types.is_numeric_dtype(df[fill_rate_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [fill_rate_col])
        kpis.append({
            "category": "🚚 Supply Chain",
            "name": "Average Fill Rate",
            "value": f"{df[fill_rate_col].mean():,.1f}%",
            "formula": f"AVG({fill_rate_col})",
            "source": fill_rate_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
