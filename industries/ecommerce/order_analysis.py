"""
Order fulfillment, status, and delivery metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_order_metrics(df):
    """Calculates order processing and fulfillment KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    order_col = first_column(df, ["order_id", "transaction_id", "invoice_id", "order_key"])
    status_col = first_column(df, ["order_status", "status", "fulfillment_status", "state"])
    quantity_col = first_column(df, ["quantity", "items", "item_count", "units", "qty"])
    order_value_col = first_column(df, ["order_value", "revenue", "sales", "total_amount", "gmv"])
    order_date_col = first_column(df, ["order_date", "date", "transaction_date", "timestamp", "created_at"])
    ship_date_col = first_column(df, ["ship_date", "shipped_date", "dispatch_date", "fulfillment_date"])
    
    if not order_col and not order_value_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [order_col, status_col, quantity_col, order_value_col, order_date_col, ship_date_col] if col])
    
    # Total orders
    if order_col:
        total_orders = df[order_col].nunique()
        
        kpis.append(safe_kpi(
            category="📑 Order Analysis",
            name="Total Orders",
            value=f"{total_orders:,}",
            formula="Count(Distinct Order IDs)",
            source=f"`{order_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Order value metrics
    if order_value_col and pd.api.types.is_numeric_dtype(df[order_value_col]):
        valid_orders = df[order_value_col].dropna()
        
        if not valid_orders.empty:
            total_revenue = valid_orders.sum()
            avg_order_value = valid_orders.mean()
            median_order_value = valid_orders.median()
            
            kpis.append(safe_kpi(
                category="📑 Order Analysis",
                name="Total Order Value",
                value=f"${total_revenue:,.2f}",
                formula="Sum(Order Values)",
                source=f"`{order_value_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="📑 Order Analysis",
                name="Avg Order Value",
                value=f"${avg_order_value:,.2f}",
                formula="Mean(Order Value)",
                source=f"`{order_value_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="📑 Order Analysis",
                name="Median Order Value",
                value=f"${median_order_value:,.2f}",
                formula="Median(Order Value)",
                source=f"`{order_value_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Items per order
    if quantity_col and pd.api.types.is_numeric_dtype(df[quantity_col]):
        valid_qty = df[quantity_col].dropna()
        
        if not valid_qty.empty:
            avg_items = valid_qty.mean()
            
            kpis.append(safe_kpi(
                category="📑 Order Analysis",
                name="Avg Items per Order",
                value=f"{avg_items:.2f}",
                formula="Mean(Item Count)",
                source=f"`{quantity_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Order status
    if status_col:
        status_lower = df[status_col].astype(str).str.lower()
        
        cancelled = status_lower.isin(['cancelled', 'canceled', 'void', 'rejected']).sum()
        completed = status_lower.isin(['completed', 'delivered', 'fulfilled', 'shipped']).sum()
        pending = status_lower.isin(['pending', 'processing', 'processing_status']).sum()
        
        total_status_rows = len(df)
        
        cancel_rate = (cancelled / total_status_rows * 100) if total_status_rows > 0 else 0
        completion_rate = (completed / total_status_rows * 100) if total_status_rows > 0 else 0
        pending_rate = (pending / total_status_rows * 100) if total_status_rows > 0 else 0
        
        kpis.append(safe_kpi(
            category="📑 Order Analysis",
            name="Cancellation Rate",
            value=f"{cancel_rate:.2f}%",
            formula="(Cancelled / Total) * 100",
            source=f"`{status_col}`",
            confidence=conf,
            warnings="High cancellation rate" if cancel_rate > 10 else warns
        ))
        
        kpis.append(safe_kpi(
            category="📑 Order Analysis",
            name="Completion Rate",
            value=f"{completion_rate:.2f}%",
            formula="(Completed / Total) * 100",
            source=f"`{status_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📑 Order Analysis",
            name="Pending Orders %",
            value=f"{pending_rate:.2f}%",
            formula="(Pending / Total) * 100",
            source=f"`{status_col}`",
            confidence=conf,
            warnings="High pending rate" if pending_rate > 50 else warns
        ))
    
    # Shipping days (this IS elapsed time - use SemanticValidator)
    if order_date_col and ship_date_col:
        order_dates = pd.to_datetime(df[order_date_col], errors="coerce")
        ship_dates = pd.to_datetime(df[ship_date_col], errors="coerce")
        
        date_df = pd.DataFrame({
            "order_date": order_dates,
            "ship_date": ship_dates
        }).dropna()
        
        if not date_df.empty:
            transit_days = (date_df["ship_date"] - date_df["order_date"]).dt.days
            
            # Validate as duration
            is_valid, reason = SemanticValidator.is_valid_duration(transit_days)
            
            if is_valid:
                if (transit_days >= 0).all() or (transit_days >= -7).all():  # Allow slight negatives
                    valid_transit = transit_days[transit_days >= 0]
                    
                    if not valid_transit.empty:
                        avg_days = valid_transit.mean()
                        max_days = valid_transit.max()
                        
                        kpis.append(safe_kpi(
                            category="📑 Order Analysis",
                            name="Avg Days to Ship",
                            value=f"{avg_days:.2f} days",
                            formula="Mean(Ship Date - Order Date)",
                            source=f"`{order_date_col}`, `{ship_date_col}`",
                            confidence=conf,
                            warnings=warns
                        ))
                        
                        kpis.append(safe_kpi(
                            category="📑 Order Analysis",
                            name="Max Days to Ship",
                            value=f"{max_days:.0f} days",
                            formula="Max(Ship Date - Order Date)",
                            source=f"`{order_date_col}`, `{ship_date_col}`",
                            confidence=conf,
                            warnings="Very long shipping delays" if max_days > 30 else warns
                        ))
            else:
                kpis.append(safe_kpi(
                    category="📑 Order Analysis",
                    name="Shipping Metrics",
                    value="EXCLUDED",
                    formula="N/A",
                    source=f"`{order_date_col}`, `{ship_date_col}`",
                    confidence="Low",
                    warnings=f"Invalid date range: {reason}"
                ))
    
    return kpis
