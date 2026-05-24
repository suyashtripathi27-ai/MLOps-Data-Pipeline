"""
Stock levels, inventory turnover, and stockout metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_inventory_metrics(df):
    """Calculates inventory management KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    product_col = first_column(df, ["product_id", "sku", "product_code", "product_key"])
    stock_col = first_column(df, ["stock_level", "quantity_on_hand", "inventory_count", "available_qty"])
    sales_col = first_column(df, ["sales_quantity", "units_sold", "qty_sold", "quantity_sold"])
    
    if not product_col or not stock_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [product_col, stock_col, sales_col] if col])
    
    total_products = df[product_col].nunique()
    
    kpis.append(safe_kpi(
        category="📦 Inventory",
        name="Total Products",
        value=f"{total_products:,}",
        formula="Count(Distinct Products)",
        source=f"`{product_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    if pd.api.types.is_numeric_dtype(df[stock_col]):
        total_stock = df[stock_col].sum()
        avg_stock = df[stock_col].mean()
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Total Inventory Units",
            value=f"{total_stock:,.0f}",
            formula="Sum(Stock Level)",
            source=f"`{stock_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Avg Stock per Product",
            value=f"{avg_stock:,.0f}",
            formula="Mean(Stock Level)",
            source=f"`{stock_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Stockout items
        stockout_count = (df[stock_col] == 0).sum()
        stockout_rate = (stockout_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Out-of-Stock Items",
            value=f"{stockout_count:,} ({stockout_rate:.2f}%)",
            formula="Count(Stock = 0) / Total * 100",
            source=f"`{stock_col}`",
            confidence=conf,
            warnings="High stockout rate" if stockout_rate > 20 else warns
        ))
        
        # Low stock
        low_stock_threshold = df[stock_col].quantile(0.25) if len(df) > 0 else 0
        low_stock_count = (df[stock_col] < low_stock_threshold).sum()
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Low Stock Items (Bottom 25%)",
            value=f"{low_stock_count:,}",
            formula="Count(Stock < 25th Percentile)",
            source=f"`{stock_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Inventory turnover
    if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]) and pd.api.types.is_numeric_dtype(df[stock_col]):
        total_sales = df[sales_col].fillna(0).sum()
        avg_stock_val = df[stock_col].mean()
        
        turnover = (total_sales / (avg_stock_val + 0.0001)) if avg_stock_val > 0 else 0
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Inventory Turnover Ratio",
            value=f"{turnover:.2f}x",
            formula="Sum(Units Sold) / Mean(Stock)",
            source=f"`{sales_col}`, `{stock_col}`",
            confidence=conf,
            warnings="Low turnover - Excess stock" if turnover < 2 else warns
        ))
    
    return kpis
