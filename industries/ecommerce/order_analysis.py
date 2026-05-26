"""
Order fulfillment, status, and delivery metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_order_metrics(df, enable_debug=False):
    """
    Calculate order processing KPIs with optional execution tracing.
    
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
    
    order_col, order_series = engine.get_column(["order_id", "transaction_id", "invoice_id", "order_key"])
    status_col, status_series = engine.get_column(["order_status", "status", "fulfillment_status", "state"])
    quantity_col, quantity_series = engine.get_numeric(["quantity", "items", "item_count", "units", "qty"])
    order_value_col, order_value_series = engine.get_numeric(["order_value", "revenue", "sales", "total_amount", "gmv"])
    order_date_col, order_date_series = engine.get_datetime(["order_date", "date", "transaction_date", "timestamp", "created_at"])
    ship_date_col, ship_date_series = engine.get_datetime(["ship_date", "shipped_date", "dispatch_date", "fulfillment_date"])
    
    # Total orders
    if order_col is not None:
        total_orders = order_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Total Orders",
            value=f"{total_orders:,}", formula="Count(Distinct Order IDs)", source=f"`{order_col}`"
        ))
    
    # Order value metrics
    if order_value_col is not None:
        total_revenue = order_value_series.sum()
        avg_order_value = order_value_series.mean()
        median_order_value = order_value_series.median()
        
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Total Order Value",
            value=f"${total_revenue:,.2f}", formula="Sum(Order Values)", source=f"`{order_value_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Avg Order Value",
            value=f"${avg_order_value:,.2f}", formula="Mean(Order Value)", source=f"`{order_value_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Median Order Value",
            value=f"${median_order_value:,.2f}", formula="Median(Order Value)", source=f"`{order_value_col}`"
        ))
    else:
        kpis.append(engine.log_missing("📋 Order Analysis", "Order Value", "Missing numeric 'order_value'."))
    
    # Items per order
    if quantity_col is not None:
        avg_items = quantity_series.mean()
        
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Avg Items per Order",
            value=f"{avg_items:.2f}", formula="Mean(Item Count)", source=f"`{quantity_col}`"
        ))
    
    # Order status
    if status_col is not None:
        status_lower = status_series.astype(str).str.lower()
        
        cancelled = status_lower.isin(['cancelled', 'canceled', 'void', 'rejected']).sum()
        completed = status_lower.isin(['completed', 'delivered', 'fulfilled', 'shipped']).sum()
        pending = status_lower.isin(['pending', 'processing', 'processing_status']).sum()
        
        total_status_rows = len(df)
        
        cancel_rate = (cancelled / total_status_rows * 100) if total_status_rows > 0 else 0
        completion_rate = (completed / total_status_rows * 100) if total_status_rows > 0 else 0
        pending_rate = (pending / total_status_rows * 100) if total_status_rows > 0 else 0
        
        warn_msg = "High cancellation rate" if cancel_rate > 10 else "None"
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Cancellation Rate",
            value=f"{cancel_rate:.2f}%", formula="(Cancelled / Total) * 100", source=f"`{status_col}`",
            warnings=warn_msg
        ))
        
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Completion Rate",
            value=f"{completion_rate:.2f}%", formula="(Completed / Total) * 100", source=f"`{status_col}`"
        ))
        
        warn_msg = "High pending rate" if pending_rate > 50 else "None"
        kpis.append(engine.build_kpi(
            category="📋 Order Analysis", name="Pending Orders %",
            value=f"{pending_rate:.2f}%", formula="(Pending / Total) * 100", source=f"`{status_col}`",
            warnings=warn_msg
        ))
    
    # Shipping days
    if order_date_col is not None and ship_date_col is not None:
        df_temp = pd.concat([order_date_series, ship_date_series], axis=1).dropna()
        
        if len(df_temp) > 0:
            transit_days = (df_temp[ship_date_col] - df_temp[order_date_col]).dt.days
            valid_transit = transit_days[transit_days >= 0]
            
            if len(valid_transit) > 0:
                avg_days = valid_transit.mean()
                max_days = valid_transit.max()
                
                kpis.append(engine.build_kpi(
                    category="📋 Order Analysis", name="Avg Days to Ship",
                    value=f"{avg_days:.2f} days", formula="Mean(Ship Date - Order Date)", source=f"`{order_date_col}`, `{ship_date_col}`"
                ))
                
                warn_msg = "Very long shipping delays" if max_days > 30 else "None"
                kpis.append(engine.build_kpi(
                    category="📋 Order Analysis", name="Max Days to Ship",
                    value=f"{max_days:.0f} days", formula="Max(Ship Date - Order Date)", source=f"`{order_date_col}`, `{ship_date_col}`",
                    warnings=warn_msg
                ))
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
