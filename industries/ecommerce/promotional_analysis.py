"""
Promotional campaign performance and impact metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_promotion_metrics(df, enable_debug=False):
    """
    Calculate promotion effectiveness KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    promo_col, promo_series = engine.get_column(["promotion_id", "promo_id", "campaign_id", "offer_code"])
    discount_col, discount_series = engine.get_numeric(["discount", "discount_amount", "promotion_value"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "order_value", "sales", "total_sales"])
    order_col, order_series = engine.get_numeric(["orders", "order_count", "transactions"])
    
    if promo_col is not None:
        total_promos = promo_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="🎯 Promotions", name="Total Promotions",
            value=f"{total_promos}", formula="Count(Distinct Promotions)", source=f"`{promo_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🎯 Promotions", "Promotions", "Missing 'promotion_id'."))
    
    # Discount impact
    if discount_col is not None:
        total_discount = discount_series.sum()
        avg_discount_per_promo = df.groupby(promo_col)[discount_col].sum().mean() if promo_col is not None else 0
        warn_msg = "High discount impact" if total_discount > 100000 else "None"
        
        kpis.append(engine.build_kpi(
            category="🎯 Promotions", name="Total Discount Given",
            value=f"${total_discount:,.2f}" if total_discount > 100 else f"{total_discount:,.2f}",
            formula="Sum(Discount)", source=f"`{discount_col}`",
            warnings=warn_msg
        ))
        
        if avg_discount_per_promo > 0:
            kpis.append(engine.build_kpi(
                category="🎯 Promotions", name="Avg Discount per Promotion",
                value=f"${avg_discount_per_promo:,.2f}", formula="Mean(Promotion Discount)", source=f"`{promo_col}`, `{discount_col}`"
            ))
    
    # Revenue by promotion
    if revenue_col is not None:
        total_revenue = revenue_series.sum()
        
        kpis.append(engine.build_kpi(
            category="🎯 Promotions", name="Total Promotion Revenue",
            value=f"${total_revenue:,.2f}", formula="Sum(Revenue in Promos)", source=f"`{revenue_col}`"
        ))
        
        if promo_col is not None:
            promo_revenue = df.groupby(promo_col)[revenue_col].sum().sort_values(ascending=False)
            if len(promo_revenue) > 0:
                top_promo = promo_revenue.idxmax()
                top_promo_rev = promo_revenue.max()
                
                kpis.append(engine.build_kpi(
                    category="🎯 Promotions", name="Top Promotion",
                    value=f"{top_promo} (${top_promo_rev:,.2f})", formula="Promotion with max revenue", source=f"`{promo_col}`, `{revenue_col}`"
                ))
    
    # Orders by promotion
    if order_col is not None:
        total_orders = order_series.sum()
        avg_orders_per_promo = df.groupby(promo_col)[order_col].sum().mean() if promo_col is not None else 0
        
        kpis.append(engine.build_kpi(
            category="🎯 Promotions", name="Total Orders with Promotions",
            value=f"{total_orders:,}", formula="Sum(Orders)", source=f"`{order_col}`"
        ))
        
        if avg_orders_per_promo > 0:
            kpis.append(engine.build_kpi(
                category="🎯 Promotions", name="Avg Orders per Promotion",
                value=f"{avg_orders_per_promo:,.0f}", formula="Mean(Promotion Orders)", source=f"`{promo_col}`, `{order_col}`"
            ))
    
    # ROI if discount and revenue exist
    if discount_col is not None and revenue_col is not None:
        total_discount = discount_series.sum()
        total_revenue = revenue_series.sum()
        
        net_benefit = total_revenue - total_discount
        roi = (net_benefit / total_discount * 100) if total_discount > 0 else 0
        warn_msg = "Negative ROI" if roi < 0 else "None"
        
        kpis.append(engine.build_kpi(
            category="🎯 Promotions", name="Promotion ROI",
            value=f"{roi:.2f}%", formula="((Revenue - Discount) / Discount) * 100", source=f"`{revenue_col}`, `{discount_col}`",
            warnings=warn_msg
        ))
  
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
