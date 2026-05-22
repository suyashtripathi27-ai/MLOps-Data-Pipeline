from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _safe_kpi(name, value, formula, source, confidence, warnings):
    return {
        "category": "🚚 Supply Chain",
        "name": name,
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warnings": warnings,
    }


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_supply_chain_metrics(df):
    """Calculates procurement and fulfillment KPIs."""
    kpis = []

    lead_col = _first_column(df, ["lead_time_days", "supplier_lead_time", "procurement_lead_time"])
    stockout_col = _first_column(df, ["stockout_events", "stockout_count"])
    orders_col = _first_column(df, ["total_orders", "total_shipments", "orders_count"])
    ontime_col = _first_column(df, ["on_time_deliveries", "on_time_shipments"])

    if lead_col:
        lead_valid, lead_reason = SemanticValidator.is_valid_duration(df[lead_col])
        if lead_valid:
            conf, warns = evaluate_kpi_confidence(df, [lead_col])
            kpis.append(
                _safe_kpi(
                    "Average Lead Time",
                    f"{df[lead_col].dropna().mean():,.2f} days",
                    "Mean(lead_time_days)",
                    f"`{lead_col}`",
                    conf,
                    warns,
                )
            )
        else:
            kpis.append(_safe_kpi("Average Lead Time", "EXCLUDED", "N/A", f"`{lead_col}`", "Low", lead_reason))

    if stockout_col and orders_col:
        total_orders = df[orders_col].dropna().sum()
        total_stockouts = df[stockout_col].dropna().sum()
        if total_orders > 0:
            conf, warns = evaluate_kpi_confidence(df, [stockout_col, orders_col])
            kpis.append(
                _safe_kpi(
                    "Stockout Rate",
                    f"{((total_stockouts / total_orders) * 100):.2f}%",
                    "(Stockout Events / Total Orders) * 100",
                    f"`{stockout_col}`, `{orders_col}`",
                    conf,
                    warns,
                )
            )

    if ontime_col and orders_col:
        total_orders = df[orders_col].dropna().sum()
        total_ontime = df[ontime_col].dropna().sum()
        if total_orders > 0:
            conf, warns = evaluate_kpi_confidence(df, [ontime_col, orders_col])
            kpis.append(
                _safe_kpi(
                    "On-Time Delivery Rate",
                    f"{((total_ontime / total_orders) * 100):.2f}%",
                    "(On-Time Deliveries / Total Orders) * 100",
                    f"`{ontime_col}`, `{orders_col}`",
                    conf,
                    warns,
                )
            )

    return kpis
