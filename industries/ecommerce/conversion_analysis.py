"""
Funnel analysis, conversion rates, and customer journey metrics.
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

def calc_conversion_metrics(df, enable_debug=False):
    """
    Calculate conversion funnel KPIs with optional execution tracing.
    
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
    
    sessions_col, sessions_series = engine.get_numeric(["sessions", "visits", "visitors", "unique_visitors", "traffic"])
    orders_col, orders_series = engine.get_numeric(["orders", "order_count", "transactions", "completed_orders"])
    cart_col, cart_series = engine.get_numeric(["cart_additions", "add_to_cart", "cart_events", "cart_count"])
    checkout_col, checkout_series = engine.get_numeric(["checkout_starts", "checkout_sessions", "initiated_checkout"])
    conversion_col, conversion_series = engine.get_numeric(["conversion_rate", "session_conversion_rate", "purchase_rate"])
    
    # Sessions to Orders conversion
    if sessions_col is not None and orders_col is not None:
        total_sessions = sessions_series.sum()
        total_orders = orders_series.sum()
        conversion_rate = (total_orders / total_sessions * 100) if total_sessions > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🔁 Conversion", name="Session Conversion Rate",
            value=f"{conversion_rate:.2f}%", formula="(Orders / Sessions) * 100", source=f"`{sessions_col}`, `{orders_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🔁 Conversion", "Session Conversion", "Missing numeric 'sessions' or 'orders'."))
    
    # Reported conversion rate
    if conversion_col is not None:
        avg_conversion = conversion_series.mean()
        
        kpis.append(engine.build_kpi(
            category="🔁 Conversion", name="Reported Conversion Rate",
            value=f"{avg_conversion:.2f}%", formula="Mean(Conversion Rate)", source=f"`{conversion_col}`"
        ))
    
    # Cart to Checkout
    if cart_col is not None and checkout_col is not None:
        cart_total = cart_series.sum()
        checkout_total = checkout_series.sum()
        cart_to_checkout = (checkout_total / cart_total * 100) if cart_total > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🔁 Conversion", name="Cart-to-Checkout Rate",
            value=f"{cart_to_checkout:.2f}%", formula="(Checkout / Cart) * 100", source=f"`{cart_col}`, `{checkout_col}`"
        ))
    
    # Sessions to Cart Add
    if sessions_col is not None and cart_col is not None:
        sessions_total = sessions_series.sum()
        cart_total = cart_series.sum()
        cart_rate = (cart_total / sessions_total * 100) if sessions_total > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🔁 Conversion", name="Cart Add Rate",
            value=f"{cart_rate:.2f}%", formula="(Cart Events / Sessions) * 100", source=f"`{sessions_col}`, `{cart_col}`"
        ))
    
    # Funnel drop-off
    if sessions_col is not None and orders_col is not None:
        sessions_total = sessions_series.sum()
        orders_total = orders_series.sum()
        funnel_gap = ((sessions_total - orders_total) / sessions_total * 100) if sessions_total > 0 else 0
        warn_msg = "High drop-off rate" if funnel_gap > 95 else "None"
        
        kpis.append(engine.build_kpi(
            category="🔁 Conversion", name="Funnel Drop-off %",
            value=f"{funnel_gap:.2f}%", formula="((Sessions - Orders) / Sessions) * 100", source=f"`{sessions_col}`, `{orders_col}`",
            warnings=warn_msg
        ))
    
    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
