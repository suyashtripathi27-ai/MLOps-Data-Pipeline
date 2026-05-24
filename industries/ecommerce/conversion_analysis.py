"""
Funnel analysis, conversion rates, and customer journey metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_conversion_metrics(df):
    """Calculates conversion funnel and rate KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    sessions_col = first_column(df, ["sessions", "visits", "visitors", "unique_visitors", "traffic"])
    orders_col = first_column(df, ["orders", "order_count", "transactions", "completed_orders"])
    cart_col = first_column(df, ["cart_additions", "add_to_cart", "cart_events", "cart_count"])
    checkout_col = first_column(df, ["checkout_starts", "checkout_sessions", "initiated_checkout"])
    conversion_col = first_column(df, ["conversion_rate", "session_conversion_rate", "purchase_rate"])
    
    if not sessions_col and not conversion_col and not orders_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [sessions_col, orders_col, cart_col, checkout_col, conversion_col] if col])
    
    # Sessions to Orders conversion
    if sessions_col and orders_col and pd.api.types.is_numeric_dtype(df[sessions_col]) and pd.api.types.is_numeric_dtype(df[orders_col]):
        sessions = df[sessions_col].fillna(0)
        orders = df[orders_col].fillna(0)
        total_sessions = sessions.sum()
        total_orders = orders.sum()
        
        conversion_rate = (total_orders / total_sessions * 100) if total_sessions > 0 else 0
        
        kpis.append(safe_kpi(
            category="🔁 Conversion",
            name="Session Conversion Rate",
            value=f"{conversion_rate:.2f}%",
            formula="(Orders / Sessions) * 100",
            source=f"`{sessions_col}`, `{orders_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Reported conversion rate
    if conversion_col and pd.api.types.is_numeric_dtype(df[conversion_col]):
        valid_conv = df[conversion_col].dropna()
        
        if not valid_conv.empty:
            avg_conversion = valid_conv.mean()
            
            kpis.append(safe_kpi(
                category="🔁 Conversion",
                name="Reported Conversion Rate",
                value=f"{avg_conversion:.2f}%",
                formula="Mean(Conversion Rate)",
                source=f"`{conversion_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Cart to Checkout
    if cart_col and checkout_col and pd.api.types.is_numeric_dtype(df[cart_col]) and pd.api.types.is_numeric_dtype(df[checkout_col]):
        cart_total = df[cart_col].fillna(0).sum()
        checkout_total = df[checkout_col].fillna(0).sum()
        
        cart_to_checkout = (checkout_total / cart_total * 100) if cart_total > 0 else 0
        
        kpis.append(safe_kpi(
            category="🔁 Conversion",
            name="Cart-to-Checkout Rate",
            value=f"{cart_to_checkout:.2f}%",
            formula="(Checkout / Cart) * 100",
            source=f"`{cart_col}`, `{checkout_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Sessions to Cart Add
    if sessions_col and cart_col and pd.api.types.is_numeric_dtype(df[sessions_col]) and pd.api.types.is_numeric_dtype(df[cart_col]):
        sessions_total = df[sessions_col].fillna(0).sum()
        cart_total = df[cart_col].fillna(0).sum()
        
        cart_rate = (cart_total / sessions_total * 100) if sessions_total > 0 else 0
        
        kpis.append(safe_kpi(
            category="🔁 Conversion",
            name="Cart Add Rate",
            value=f"{cart_rate:.2f}%",
            formula="(Cart Events / Sessions) * 100",
            source=f"`{sessions_col}`, `{cart_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Funnel drop-off
    if sessions_col and orders_col and pd.api.types.is_numeric_dtype(df[sessions_col]) and pd.api.types.is_numeric_dtype(df[orders_col]):
        sessions_total = df[sessions_col].fillna(0).sum()
        orders_total = df[orders_col].fillna(0).sum()
        
        funnel_gap = ((sessions_total - orders_total) / sessions_total * 100) if sessions_total > 0 else 0
        
        kpis.append(safe_kpi(
            category="🔁 Conversion",
            name="Funnel Drop-off %",
            value=f"{funnel_gap:.2f}%",
            formula="((Sessions - Orders) / Sessions) * 100",
            source=f"`{sessions_col}`, `{orders_col}`",
            confidence=conf,
            warnings="High drop-off rate" if funnel_gap > 95 else warns
        ))
    
    return kpis
