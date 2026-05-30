"""
Promotional effectiveness, lift, and ROI metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_promotion_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    promo_col, promo_series = engine.get_column(["promotion_id", "promo_id", "campaign_id", "offer_id"])
    sales_col, sales_series = engine.get_numeric(["sales", "revenue", "order_value", "sales_amount"])
    disc_col, disc_series = engine.get_numeric(["discount", "promotion_discount", "discount_value"])
    qty_col, qty_series = engine.get_numeric(["quantity", "units_sold", "sales_qty"])
    
    if promo_col is not None:
        kpis.append(engine.build_kpi("🎯 Promotions", "Total Active Promotions", f"{promo_series.nunique()}", "Count(Distinct Promos)", f"`{promo_col}`"))
        
        if sales_col is not None:
            promo_sales_df = pd.concat([promo_series, sales_series], axis=1).dropna()
            if len(promo_sales_df) > 0:
                promo_grouped = promo_sales_df.groupby(promo_col)[sales_col].sum().sort_values(ascending=False)
                kpis.append(engine.build_kpi("🎯 Promotions", "Total Promotion Sales", f"${promo_grouped.sum():,.2f}", "Sum(Sales in Promos)", f"`{sales_col}`"))
                kpis.append(engine.build_kpi("🎯 Promotions", "Top Promotion", f"{promo_grouped.idxmax()} (${promo_grouped.max():,.2f})", "Promo with max sales", f"`{promo_col}`, `{sales_col}`"))
    else:
        kpis.append(engine.log_missing("🎯 Promotions", "Promotions", "Missing 'promotion_id'."))

    if disc_col is not None:
        disc_clean = disc_series.dropna()
        if len(disc_clean) > 0:
            kpis.append(engine.build_kpi("🎯 Promotions", "Total Discount Given", f"${disc_clean.sum():,.2f}", "Sum(Discount)", f"`{disc_col}`"))
            kpis.append(engine.build_kpi("🎯 Promotions", "Avg Discount per Promotion", f"${disc_clean.mean():,.2f}", "Mean(Discount)", f"`{disc_col}`"))
            
            if sales_col is not None:
                roi_df = pd.concat([sales_series, disc_series], axis=1).dropna()
                if len(roi_df) > 0:
                    tot_s = roi_df[sales_col].sum()
                    tot_d = roi_df[disc_col].sum()
                    roi = ((tot_s - tot_d) / tot_d * 100) if tot_d > 0 else 0
                    kpis.append(engine.build_kpi("🎯 Promotions", "Promotion ROI", f"{roi:.2f}%", "((Sales - Discount) / Discount) * 100", f"`{sales_col}`, `{disc_col}`", warnings="Negative ROI" if roi < 0 else "None"))

    if qty_col is not None:
        qty_clean = qty_series.dropna()
        if len(qty_clean) > 0:
            kpis.append(engine.build_kpi("🎯 Promotions", "Total Units Sold in Promotions", f"{qty_clean.sum():,.0f}", "Sum(Qty)", f"`{qty_col}`"))

    if enable_debug: engine.print_execution_log()
    return kpis
