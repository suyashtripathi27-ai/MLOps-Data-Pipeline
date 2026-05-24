"""
Promotional campaign performance and impact metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_promotion_metrics(df):
    """Calculates promotion effectiveness KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    promo_col = first_column(df, ["promotion_id", "promo_id", "campaign_id", "offer_code"])
    discount_col = first_column(df, ["discount", "discount_amount", "promotion_value"])
    revenue_col = first_column(df, ["revenue", "order_value", "sales", "total_sales"])
    order_col = first_column(df, ["orders", "order_count", "transactions"])
    
    if not promo_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [promo_col, discount_col, revenue_col, order_col] if col])
    
    # Total promotions
    total_promos = df[promo_col].nunique()
    
    kpis.append(safe_kpi(
        category="🎯 Promotions",
        name="Total Promotions",
        value=f"{total_promos}",
        formula="Count(Distinct Promotions)",
        source=f"`{promo_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Discount impact
    if discount_col and pd.api.types.is_numeric_dtype(df[discount_col]):
        total_discount = df[discount_col].sum()
        avg_discount_per_promo = df.groupby(promo_col)[discount_col].sum().mean()
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Total Discount Given",
            value=f"${total_discount:,.2f}" if total_discount > 100 else f"{total_discount:,.2f}",
            formula="Sum(Discount)",
            source=f"`{discount_col}`",
            confidence=conf,
            warnings="High discount impact" if total_discount > 100000 else warns
        ))
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Avg Discount per Promotion",
            value=f"${avg_discount_per_promo:,.2f}",
            formula="Mean(Promotion Discount)",
            source=f"`{promo_col}`, `{discount_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Revenue by promotion
    if revenue_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_revenue = df[revenue_col].sum()
        promo_revenue = df.groupby(promo_col)[revenue_col].sum().sort_values(ascending=False)
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Total Promotion Revenue",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue in Promos)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        if not promo_revenue.empty:
            top_promo = promo_revenue.idxmax()
            top_promo_rev = promo_revenue.max()
            
            kpis.append(safe_kpi(
                category="🎯 Promotions",
                name="Top Promotion",
                value=f"{top_promo} (${top_promo_rev:,.2f})",
                formula="Promotion with max revenue",
                source=f"`{promo_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Orders by promotion
    if order_col and pd.api.types.is_numeric_dtype(df[order_col]):
        total_orders = df[order_col].sum()
        avg_orders_per_promo = df.groupby(promo_col)[order_col].sum().mean()
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Total Orders with Promotions",
            value=f"{total_orders:,}",
            formula="Sum(Orders)",
            source=f"`{order_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Avg Orders per Promotion",
            value=f"{avg_orders_per_promo:,.0f}",
            formula="Mean(Promotion Orders)",
            source=f"`{promo_col}`, `{order_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # ROI if discount and revenue exist
    if discount_col and revenue_col and pd.api.types.is_numeric_dtype(df[discount_col]) and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_discount = df[discount_col].sum()
        total_revenue = df[revenue_col].sum()
        
        net_benefit = total_revenue - total_discount
        roi = (net_benefit / total_discount * 100) if total_discount > 0 else 0
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Promotion ROI",
            value=f"{roi:.2f}%",
            formula="((Revenue - Discount) / Discount) * 100",
            source=f"`{revenue_col}`, `{discount_col}`",
            confidence=conf,
            warnings="Negative ROI" if roi < 0 else warns
        ))
    
    return kpis
