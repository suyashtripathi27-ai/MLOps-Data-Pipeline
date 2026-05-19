import pandas as pd
from .reliability import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_promotion_metrics(df):
    """Calculates promotion lift, ROI, and conversion KPIs."""
    kpis = []
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    promo_col = _first_column(df, ["is_promo", "promotion_flag", "promo_flag"])
    discount_cost_col = _first_column(df, ["discount_amount", "promo_cost", "campaign_cost"])
    conversion_col = _first_column(df, ["campaign_conversion", "conversion_rate", "promo_conversion"])
    if not revenue_col or not promo_col:
        return kpis

    promo_series = df[promo_col].astype(str).str.lower().isin(["true", "1", "yes", "y"])
    analysis_df = df[[revenue_col]].copy()
    analysis_df["is_promo"] = promo_series
    analysis_df = analysis_df.dropna(subset=[revenue_col])
    if analysis_df.empty:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [promo_col, revenue_col] + ([discount_cost_col] if discount_cost_col else []))
    promo_avg = analysis_df.loc[analysis_df["is_promo"], revenue_col].mean() if analysis_df["is_promo"].any() else 0
    non_promo_avg = analysis_df.loc[~analysis_df["is_promo"], revenue_col].mean() if (~analysis_df["is_promo"]).any() else 0
    sales_lift = ((promo_avg - non_promo_avg) / non_promo_avg * 100) if non_promo_avg else 0
    kpis.append({
        "category": "🎯 Promotion Analysis",
        "name": "Promo Sales Lift",
        "value": f"{sales_lift:.2f}%",
        "formula": "((Promo Avg Sales - Non-Promo Avg Sales) / Non-Promo Avg Sales) * 100",
        "source": f"`{promo_col}`, `{revenue_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if discount_cost_col:
        promo_revenue = analysis_df.loc[analysis_df["is_promo"], revenue_col].sum()
        promo_cost = df.loc[promo_series, discount_cost_col].fillna(0).sum()
        roi = ((promo_revenue - promo_cost) / promo_cost) if promo_cost > 0 else 0
        kpis.append({
            "category": "🎯 Promotion Analysis",
            "name": "Discount ROI",
            "value": f"{roi:.2f}x",
            "formula": "(Promo Revenue - Promo Cost) / Promo Cost",
            "source": f"`{revenue_col}`, `{discount_cost_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if conversion_col:
        conversion_rate = df[conversion_col].dropna().mean()
        kpis.append({
            "category": "🎯 Promotion Analysis",
            "name": "Campaign Conversion",
            "value": f"{conversion_rate:.2f}%",
            "formula": "Mean(Campaign Conversion %)",
            "source": f"`{conversion_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
