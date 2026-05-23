import pandas as pd
from .common import bool_mask, confidence_for, first_column, safe_kpi
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def calc_conversion_metrics(df):
    kpis = []
    sessions_col = first_column(df, ["sessions", "visits", "visitors", "unique_visitors", "traffic", "page_sessions"])
    orders_col = first_column(df, ["orders", "order_count", "transactions", "completed_orders"])
    cart_col = first_column(df, ["cart_additions", "add_to_cart", "cart_events", "cart_count"])
    checkout_col = first_column(df, ["checkout_starts", "checkout_sessions", "initiated_checkout"])
    conversion_col = first_column(df, ["conversion_rate", "session_conversion_rate", "purchase_rate"])
    if not sessions_col and not conversion_col:
        return kpis

    conf, warns = confidence_for(df, [sessions_col, orders_col, cart_col, checkout_col, conversion_col])

    if sessions_col and orders_col:
        sessions = df[sessions_col].fillna(0)
        orders = df[orders_col].fillna(0)
        conversion_rate = (orders.sum() / sessions.sum() * 100) if sessions.sum() > 0 else 0
        kpis.append(safe_kpi("🔁 Conversion Analysis", "Session Conversion Rate", f"{conversion_rate:.2f}%", "Orders / Sessions * 100", f"`{sessions_col}`, `{orders_col}`", conf, warns))

    if conversion_col:
        conversion_rate = df[conversion_col].dropna().mean()
        kpis.append(safe_kpi("🔁 Conversion Analysis", "Reported Conversion Rate", f"{conversion_rate:.2f}%", "Mean(Conversion Rate)", f"`{conversion_col}`", conf, warns))

    if cart_col and checkout_col:
        cart_total = df[cart_col].fillna(0).sum()
        checkout_total = df[checkout_col].fillna(0).sum()
        cart_to_checkout = (checkout_total / cart_total * 100) if cart_total > 0 else 0
        kpis.append(safe_kpi("🔁 Conversion Analysis", "Cart-to-Checkout Rate", f"{cart_to_checkout:.2f}%", "Checkout Events / Cart Events * 100", f"`{cart_col}`, `{checkout_col}`", conf, warns))

    if sessions_col and cart_col:
        cart_rate = (df[cart_col].fillna(0).sum() / df[sessions_col].fillna(0).sum() * 100) if df[sessions_col].fillna(0).sum() > 0 else 0
        kpis.append(safe_kpi("🔁 Conversion Analysis", "Cart Add Rate", f"{cart_rate:.2f}%", "Cart Events / Sessions * 100", f"`{sessions_col}`, `{cart_col}`", conf, warns))

    if sessions_col and orders_col:
        funnel_gap = ((df[sessions_col].fillna(0).sum() - df[orders_col].fillna(0).sum()) / df[sessions_col].fillna(0).sum() * 100) if df[sessions_col].fillna(0).sum() > 0 else 0
        kpis.append(safe_kpi("🔁 Conversion Analysis", "Funnel Drop-off", f"{funnel_gap:.2f}%", "(Sessions - Orders) / Sessions * 100", f"`{sessions_col}`, `{orders_col}`", conf, warns))

    return kpis
