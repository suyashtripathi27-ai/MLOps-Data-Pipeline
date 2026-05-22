import pandas as pd
from .common import confidence_for, first_column, safe_kpi
from utils.validator import SemanticValidator


def calc_order_metrics(df):
    kpis = []
    order_col = first_column(df, ["order_id", "transaction_id", "invoice_id"])
    status_col = first_column(df, ["order_status", "status", "fulfillment_status"])
    quantity_col = first_column(df, ["quantity", "items", "item_count", "units"])
    order_value_col = first_column(df, ["order_value", "revenue", "sales", "total_amount"])
    order_date_col = first_column(df, ["order_date", "date", "transaction_date", "timestamp"])
    ship_date_col = first_column(df, ["ship_date", "shipped_date", "dispatch_date"])

    if not order_col and not order_value_col:
        return kpis

    conf, warns = confidence_for(df, [order_col, status_col, quantity_col, order_value_col, order_date_col, ship_date_col])

    if order_col:
        total_orders = df[order_col].nunique(dropna=True)
        kpis.append(safe_kpi("📑 Order Analysis", "Total Orders", f"{total_orders:,}", "Distinct(Order IDs)", f"`{order_col}`", conf, warns))

    if order_value_col:
        kpis.append(safe_kpi("📑 Order Analysis", "Avg Order Value", f"${df[order_value_col].dropna().mean():,.2f}", "Mean(Order Value)", f"`{order_value_col}`", conf, warns))

    if quantity_col:
        kpis.append(safe_kpi("📑 Order Analysis", "Avg Items per Order", f"{df[quantity_col].dropna().mean():.2f}", "Mean(Items)", f"`{quantity_col}`", conf, warns))

    if status_col:
        status_series = df[status_col].astype(str).str.lower()
        cancel_rate = status_series.isin(["cancelled", "canceled", "void", "refunded"]).mean() * 100
        completion_rate = status_series.isin(["completed", "delivered", "fulfilled", "shipped"]).mean() * 100
        kpis.append(safe_kpi("📑 Order Analysis", "Cancellation Rate", f"{cancel_rate:.2f}%", "Cancelled Orders / Total Orders * 100", f"`{status_col}`", conf, warns))
        kpis.append(safe_kpi("📑 Order Analysis", "Completion Rate", f"{completion_rate:.2f}%", "Completed Orders / Total Orders * 100", f"`{status_col}`", conf, warns))

    if order_date_col and ship_date_col:
        order_dates = pd.to_datetime(df[order_date_col], errors="coerce")
        ship_dates = pd.to_datetime(df[ship_date_col], errors="coerce")
        valid_dates = pd.DataFrame({"order_date": order_dates, "ship_date": ship_dates}).dropna()
        if not valid_dates.empty:
            transit_days = (valid_dates["ship_date"] - valid_dates["order_date"]).dt.days
            if not transit_days.empty:
                valid_transit, reason = SemanticValidator.is_valid_duration(transit_days)
                if valid_transit:
                    kpis.append(safe_kpi("📑 Order Analysis", "Avg Days to Ship", f"{transit_days.mean():.2f} days", "Mean(Ship Date - Order Date)", f"`{order_date_col}`, `{ship_date_col}`", conf, warns))
                else:
                    kpis.append(safe_kpi("📑 Order Analysis", "Order Transit Metrics", "EXCLUDED", "N/A", f"`{order_date_col}`, `{ship_date_col}`", "Low", reason))

    return kpis
