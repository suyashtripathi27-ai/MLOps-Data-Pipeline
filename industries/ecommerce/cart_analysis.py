"""
Shopping cart metrics and abandonment analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
# Moderate thresholds - focus on growth velocity vs strict compliance
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,        # ✅ Moderate - tech platforms have data quality
    "score_deduction_for_warning": 12,  # ✅ Lower penalty - more lenient than banking
    "low_confidence_threshold": 35,     # ✅ Higher threshold = harder to flag "Low"
}

def calc_cart_metrics(df, enable_debug=False):
    """
    Calculate cart-level KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    # ✅ OPTION 2: Initialize with ecommerce industry config
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    
    # ✅ OPTION 1: Enable tracing for enterprise observability
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    cart_value_col, cart_value_series = engine.get_numeric(["cart_value", "basket_value", "cart_total", "basket_total"])
    abandoned_rate_col, abandoned_rate_series = engine.get_numeric(["cart_abandonment_rate", "abandonment_rate", "abandoned_rate"])
    cart_items_col, cart_items_series = engine.get_numeric(["cart_items", "items_in_cart", "basket_items"])
    
    if cart_value_col is not None:
        kpis.append(engine.build_kpi(
            category="🛑 Cart Analysis", name="Avg Cart Value",
            value=f"${cart_value_series.mean():,.2f}", formula="Mean(Cart Value)", source=f"`{cart_value_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="🛑 Cart Analysis", name="Median Cart Value",
            value=f"${cart_value_series.median():,.2f}", formula="Median(Cart Value)", source=f"`{cart_value_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="🛑 Cart Analysis", name="Max Cart Value",
            value=f"${cart_value_series.max():,.2f}", formula="Max(Cart Value)", source=f"`{cart_value_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🛑 Cart Analysis", "Cart Value", "Missing numeric 'cart_value' column."))
    
    if abandoned_rate_col is not None:
        avg_abandonment = abandoned_rate_series.mean()
        warn_msg = "High abandonment rate" if avg_abandonment > 70 else "None"
        
        kpis.append(engine.build_kpi(
            category="🛑 Cart Analysis", name="Cart Abandonment Rate",
            value=f"{avg_abandonment:.2f}%", formula="Mean(Abandonment Rate)", source=f"`{abandoned_rate_col}`",
            warnings=warn_msg
        ))
    else:
        kpis.append(engine.log_missing("🛑 Cart Analysis", "Abandonment Rate", "Missing numeric 'abandonment_rate' column."))
    
    if cart_items_col is not None:
        avg_items = cart_items_series.mean()
        
        kpis.append(engine.build_kpi(
            category="🛑 Cart Analysis", name="Avg Items per Cart",
            value=f"{avg_items:.2f}", formula="Mean(Cart Items)", source=f"`{cart_items_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🛑 Cart Analysis", "Items per Cart", "Missing numeric 'cart_items' column."))
    
    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
