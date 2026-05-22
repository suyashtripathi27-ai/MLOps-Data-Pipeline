import pandas as pd
from .common import bool_mask, confidence_for, first_column, safe_kpi
from utils.validator import SemanticValidator


def calc_promotion_metrics(df):
    kpis = []
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "total_sales"])
    promo_col = first_column(df, ["is_promo", "promotion_flag", "promo_flag", "campaign_flag"])
    discount_cost_col = first_column(df, ["discount_amount", "promo_cost", "campaign_cost"])
    conversion_col = first_column(df, ["campaign_conversion", "conversion_rate", "promo_conversion"])
    if not revenue_col or not promo_col:
        return kpis

    promo_series = bool_mask(df[promo_col])
    analysis_df = df[[revenue_col]].copy()
    analysis_df["is_promo"] = promo_series
    analysis_df = analysis_df.dropna(subset=[revenue_col])
    if analysis_df.empty:
        return kpis

    conf, warns = confidence_for(df, [revenue_col, promo_col] + ([discount_cost_col] if discount_cost_col else []) + ([conversion_col] if conversion_col else []))
    promo_avg = analysis_df.loc[analysis_df["is_promo"], revenue_col].mean() if analysis_df["is_promo"].any() else 0
    non_promo_avg = analysis_df.loc[~analysis_df["is_promo"], revenue_col].mean() if (~analysis_df["is_promo"]).any() else 0
    sales_lift = ((promo_avg - non_promo_avg) / non_promo_avg * 100) if non_promo_avg else 0
    kpis.append(safe_kpi("🎯 Promotion Analysis", "Promo Sales Lift", f"{sales_lift:.2f}%", "((Promo Avg Sales - Non-Promo Avg Sales) / Non-Promo Avg Sales) * 100", f"`{promo_col}`, `{revenue_col}`", conf, warns))

    if discount_cost_col:
        promo_revenue = analysis_df.loc[analysis_df["is_promo"], revenue_col].sum()
        promo_cost = df.loc[promo_series, discount_cost_col].fillna(0).sum()
        roi = ((promo_revenue - promo_cost) / promo_cost) if promo_cost > 0 else 0
        kpis.append(safe_kpi("🎯 Promotion Analysis", "Discount ROI", f"{roi:.2f}x", "(Promo Revenue - Promo Cost) / Promo Cost", f"`{revenue_col}`, `{discount_cost_col}`", conf, warns))

    if conversion_col:
        conversion_rate = df[conversion_col].dropna().mean()
        kpis.append(safe_kpi("🎯 Promotion Analysis", "Campaign Conversion", f"{conversion_rate:.2f}%", "Mean(Campaign Conversion %)", f"`{conversion_col}`", conf, warns))

    return kpis
