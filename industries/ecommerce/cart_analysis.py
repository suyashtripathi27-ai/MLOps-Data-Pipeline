"""
Shopping cart metrics and abandonment analysis.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_cart_metrics(df):
    """Calculates shopping cart and abandonment KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    cart_value_col = first_column(df, ["cart_value", "basket_value", "cart_total", "basket_total"])
    abandoned_rate_col = first_column(df, ["cart_abandonment_rate", "abandonment_rate", "abandoned_rate"])
    cart_items_col = first_column(df, ["cart_items", "items_in_cart", "basket_items"])
    
    if not cart_value_col and not abandoned_rate_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [cart_value_col, abandoned_rate_col, cart_items_col] if col])
    
    if cart_value_col and pd.api.types.is_numeric_dtype(df[cart_value_col]):
        valid_cart = df[cart_value_col].dropna()
        
        if not valid_cart.empty:
            avg_cart = valid_cart.mean()
            median_cart = valid_cart.median()
            max_cart = valid_cart.max()
            
            kpis.append(safe_kpi(
                category="🛍️ Cart Analysis",
                name="Avg Cart Value",
                value=f"${avg_cart:,.2f}",
                formula="Mean(Cart Value)",
                source=f"`{cart_value_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🛍️ Cart Analysis",
                name="Median Cart Value",
                value=f"${median_cart:,.2f}",
                formula="Median(Cart Value)",
                source=f"`{cart_value_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🛍️ Cart Analysis",
                name="Max Cart Value",
                value=f"${max_cart:,.2f}",
                formula="Max(Cart Value)",
                source=f"`{cart_value_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    if abandoned_rate_col and pd.api.types.is_numeric_dtype(df[abandoned_rate_col]):
        valid_abandon = df[abandoned_rate_col].dropna()
        
        if not valid_abandon.empty:
            avg_abandonment = valid_abandon.mean()
            
            kpis.append(safe_kpi(
                category="🛍️ Cart Analysis",
                name="Cart Abandonment Rate",
                value=f"{avg_abandonment:.2f}%",
                formula="Mean(Abandonment Rate)",
                source=f"`{abandoned_rate_col}`",
                confidence=conf,
                warnings="High abandonment rate" if avg_abandonment > 70 else warns
            ))
    
    if cart_items_col and pd.api.types.is_numeric_dtype(df[cart_items_col]):
        valid_items = df[cart_items_col].dropna()
        
        if not valid_items.empty:
            avg_items = valid_items.mean()
            
            kpis.append(safe_kpi(
                category="🛍️ Cart Analysis",
                name="Avg Items per Cart",
                value=f"{avg_items:.2f}",
                formula="Mean(Cart Items)",
                source=f"`{cart_items_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
