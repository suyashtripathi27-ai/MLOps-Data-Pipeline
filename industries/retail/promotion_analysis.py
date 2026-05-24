"""
Promotional effectiveness, lift, and ROI metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_promotion_metrics(df):
    """Calculates promotion effectiveness KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Promotion metrics
    promo_col = first_column(df, ["promotion_id", "promo_id", "campaign_id", "offer_id"])
    sales_col = first_column(df, ["sales", "revenue", "order_value", "sales_amount"])
    discount_col = first_column(df, ["discount", "promotion_discount", "discount_value"])
    quantity_col = first_column(df, ["quantity", "units_sold", "sales_qty"])
    
    if not promo_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [promo_col, sales_col, discount_col, quantity_col] if col])
    
    # Total promotions
    total_promos = df[promo_col].nunique()
    
    kpis.append(safe_kpi(
        category="🎯 Promotions",
        name="Total Active Promotions",
        value=f"{total_promos}",
        formula="Count(Distinct Promotions)",
        source=f"`{promo_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Sales lift
    if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        total_sales = df[sales_col].sum()
        promo_sales = df.groupby(promo_col)[sales_col].sum().sort_values(ascending=False)
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Total Promotion Sales",
            value=f"${total_sales:,.2f}",
            formula="Sum(Sales in Promotions)",
            source=f"`{sales_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        if not promo_sales.empty:
            top_promo = promo_sales.idxmax()
            top_promo_sales = promo_sales.max()
            
            kpis.append(safe_kpi(
                category="🎯 Promotions",
                name="Top Promotion",
                value=f"{top_promo} (${top_promo_sales:,.2f})",
                formula="Promotion with max sales",
                source=f"`{promo_col}`, `{sales_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Discount impact
    if discount_col and pd.api.types.is_numeric_dtype(df[discount_col]):
        total_discount = df[discount_col].sum()
        avg_discount = df[discount_col].mean()
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Total Discount Given",
            value=f"${total_discount:,.2f}",
            formula="Sum(Discount)",
            source=f"`{discount_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Avg Discount per Promotion",
            value=f"${avg_discount:,.2f}",
            formula="Mean(Discount)",
            source=f"`{discount_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # ROI calculation
    if discount_col and sales_col and pd.api.types.is_numeric_dtype(df[discount_col]) and pd.api.types.is_numeric_dtype(df[sales_col]):
        total_discount = df[discount_col].sum()
        total_sales = df[sales_col].sum()
        
        net_benefit = total_sales - total_discount
        roi = (net_benefit / total_discount * 100) if total_discount > 0 else 0
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Promotion ROI",
            value=f"{roi:.2f}%",
            formula="((Sales - Discount) / Discount) * 100",
            source=f"`{sales_col}`, `{discount_col}`",
            confidence=conf,
            warnings="Negative ROI - Losing money" if roi < 0 else "Low ROI" if roi < 50 else warns
        ))
    
    # Units sold in promotions
    if quantity_col and pd.api.types.is_numeric_dtype(df[quantity_col]):
        total_qty = df[quantity_col].sum()
        
        kpis.append(safe_kpi(
            category="🎯 Promotions",
            name="Total Units Sold in Promotions",
            value=f"{total_qty:,.0f}",
            formula="Sum(Quantity in Promos)",
            source=f"`{quantity_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
