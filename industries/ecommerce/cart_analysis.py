import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator


def calc_cart_metrics(df):
    kpis = []
    cart_value_col = first_column(df, ["cart_value", "basket_value", "cart_total", "basket_total"])
    abandoned_rate_col = first_column(df, ["cart_abandonment_rate", "abandonment_rate", "abandoned_rate"])
    cart_items_col = first_column(df, ["cart_items", "items_in_cart", "basket_items"])
    if not cart_value_col and not abandoned_rate_col:
        return kpis

    conf, warns = confidence_for(df, [cart_value_col, abandoned_rate_col, cart_items_col])

    if cart_value_col:
        if not SemanticValidator.is_valid_duration(df[cart_value_col])[0]:
            return [safe_kpi("🛍️ Cart Analysis", "Cart Metrics", "EXCLUDED", "N/A", f"`{cart_value_col}`", "Low", "Invalid cart value distribution.")]
        kpis.append(safe_kpi("🛍️ Cart Analysis", "Avg Cart Value", f"${df[cart_value_col].dropna().mean():,.2f}", "Mean(Cart Value)", f"`{cart_value_col}`", conf, warns))
        kpis.append(safe_kpi("🛍️ Cart Analysis", "Cart Value Median", f"${df[cart_value_col].dropna().median():,.2f}", "Median(Cart Value)", f"`{cart_value_col}`", conf, warns))

    if abandoned_rate_col:
        abandonment = df[abandoned_rate_col].dropna().mean()
        kpis.append(safe_kpi("🛍️ Cart Analysis", "Cart Abandonment Rate", f"{abandonment:.2f}%", "Mean(Abandonment Rate)", f"`{abandoned_rate_col}`", conf, warns))

    if cart_items_col:
        avg_items = df[cart_items_col].dropna().mean()
        kpis.append(safe_kpi("🛍️ Cart Analysis", "Avg Items per Cart", f"{avg_items:.2f}", "Mean(Cart Items)", f"`{cart_items_col}`", conf, warns))

    return kpis
