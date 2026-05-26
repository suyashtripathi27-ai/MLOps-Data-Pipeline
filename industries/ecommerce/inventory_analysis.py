"""
Stock levels, inventory turnover, and stockout metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,        
    "score_deduction_for_warning": 12,  
    "low_confidence_threshold": 35,     
}

def calc_inventory_metrics(df, enable_debug=False):
    """
    Calculate inventory management KPIs with optional execution tracing.
    
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
    
    product_col, product_series = engine.get_column(["product_id", "sku", "product_code", "product_key"])
    stock_col, stock_series = engine.get_numeric(["stock_level", "quantity_on_hand", "inventory_count", "available_qty"])
    sales_col, sales_series = engine.get_numeric(["sales_quantity", "units_sold", "qty_sold", "quantity_sold"])
    
    if product_col is not None and stock_col is not None:
        total_products = product_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="📖 Inventory", name="Total Products",
            value=f"{total_products:,}", formula="Count(Distinct Products)", source=f"`{product_col}`"
        ))
        
        total_stock = stock_series.sum()
        avg_stock = stock_series.mean()
        
        kpis.append(engine.build_kpi(
            category="📖 Inventory", name="Total Inventory Units",
            value=f"{total_stock:,.0f}", formula="Sum(Stock Level)", source=f"`{stock_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📖 Inventory", name="Avg Stock per Product",
            value=f"{avg_stock:,.0f}", formula="Mean(Stock Level)", source=f"`{stock_col}`"
        ))
        
        # Stockout items
        stockout_count = (stock_series == 0).sum()
        stockout_rate = (stockout_count / len(df) * 100) if len(df) > 0 else 0
        warn_msg = "High stockout rate" if stockout_rate > 20 else "None"
        
        kpis.append(engine.build_kpi(
            category="📖 Inventory", name="Out-of-Stock Items",
            value=f"{stockout_count:,} ({stockout_rate:.2f}%)", formula="Count(Stock = 0) / Total * 100", source=f"`{stock_col}`",
            warnings=warn_msg
        ))
        
        # Low stock
        low_stock_threshold = stock_series.quantile(0.25) if len(df) > 0 else 0
        low_stock_count = (stock_series < low_stock_threshold).sum()
        
        kpis.append(engine.build_kpi(
            category="📖 Inventory", name="Low Stock Items (Bottom 25%)",
            value=f"{low_stock_count:,}", formula="Count(Stock < 25th Percentile)", source=f"`{stock_col}`"
        ))
        
        # Inventory turnover
        if sales_col is not None:
            total_sales = sales_series.sum()
            avg_stock_val = stock_series.mean()
            turnover = (total_sales / (avg_stock_val + 0.0001)) if avg_stock_val > 0 else 0
            warn_msg = "Low turnover - Excess stock" if turnover < 2 else "None"
            
            kpis.append(engine.build_kpi(
                category="📖 Inventory", name="Inventory Turnover Ratio",
                value=f"{turnover:.2f}x", formula="Sum(Units Sold) / Mean(Stock)", source=f"`{sales_col}`, `{stock_col}`",
                warnings=warn_msg
            ))
    else:
        kpis.append(engine.log_missing("📖 Inventory", "Inventory Metrics", "Missing 'product_id' or numeric 'stock_level'."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
