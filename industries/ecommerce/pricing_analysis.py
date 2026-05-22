import pandas as pd
from .common import confidence_for, first_column, safe_kpi
from utils.validator import SemanticValidator


def calc_pricing_metrics(df):
    kpis = []
    price_col = first_column(df, ["price", "unit_price", "list_price", "sale_price", "amount"])
    discount_col = first_column(df, ["discount", "discount_rate", "markdown", "promo_discount"])
    cost_col = first_column(df, ["cost", "unit_cost", "cogs", "purchase_cost"])
    if not price_col:
        return kpis

    if not SemanticValidator.is_valid_duration(df[price_col])[0]:
        return [safe_kpi("💲 Pricing Analysis", "Pricing Metrics", "EXCLUDED", "N/A", f"`{price_col}`", "Low", "Invalid price distribution.")]

    conf, warns = confidence_for(df, [price_col, discount_col, cost_col])
    price_series = df[price_col].dropna()
    if price_series.empty:
        return kpis

    kpis.append(safe_kpi("💲 Pricing Analysis", "Avg Selling Price", f"${price_series.mean():,.2f}", "Mean(Price)", f"`{price_col}`", conf, warns))
    kpis.append(safe_kpi("💲 Pricing Analysis", "Price Median", f"${price_series.median():,.2f}", "Median(Price)", f"`{price_col}`", conf, warns))
    kpis.append(safe_kpi("💲 Pricing Analysis", "Price Dispersion", f"{price_series.std(ddof=0):.2f}", "StdDev(Price)", f"`{price_col}`", conf, warns))

    if discount_col:
        discount_series = df[discount_col].dropna()
        discount_value = discount_series.mean()
        kpis.append(safe_kpi("💲 Pricing Analysis", "Average Discount", f"{discount_value:.2f}%", "Mean(Discount)", f"`{discount_col}`", conf, warns))

    if cost_col:
        margin = ((price_series.mean() - df[cost_col].dropna().mean()) / price_series.mean() * 100) if price_series.mean() > 0 else 0
        kpis.append(safe_kpi("💲 Pricing Analysis", "Gross Margin Proxy", f"{margin:.2f}%", "(Avg Price - Avg Cost) / Avg Price * 100", f"`{price_col}`, `{cost_col}`", conf, warns))

    return kpis
