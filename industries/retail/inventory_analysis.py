"""
Inventory turnover, stock levels, dead stock, and stockout metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_inventory_metrics(df):
    """Calculates inventory and stock management KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Inventory metrics are COUNT (units), not time
    inventory_col = first_column(df, ["inventory_level", "stock_level", "on_hand_inventory", "stock_on_hand"])
    sold_col = first_column(df, ["units_sold", "quantity_sold", "sales_units"])
    received_col = first_column(df, ["units_received", "quantity_received", "stock_received"])
    cogs_col = first_column(df, ["cogs", "cost_of_goods_sold", "cost"])
    stockout_col = first_column(df, ["stockout_flag", "is_stockout", "out_of_stock"])
    
    if not inventory_col:
        return kpis
    
    # Inventory is COUNT (units), not duration
    if not pd.api.types.is_numeric_dtype(df[inventory_col]):
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Inventory Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{inventory_col}`",
            confidence="Low",
            warnings="Inventory column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [inventory_col, sold_col, received_col, cogs_col, stockout_col] if col])
    
    # Inventory levels
    valid_inventory = df[inventory_col].dropna()
    
    if not valid_inventory.empty:
        avg_inventory = valid_inventory.mean()
        total_inventory = valid_inventory.sum()
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Total Inventory Units",
            value=f"{total_inventory:,.0f}",
            formula="Sum(Inventory Level)",
            source=f"`{inventory_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Avg Inventory Level",
            value=f"{avg_inventory:,.0f}",
            formula="Mean(Inventory Level)",
            source=f"`{inventory_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Inventory turnover
    if avg_inventory and avg_inventory > 0:
        if sold_col and pd.api.types.is_numeric_dtype(df[sold_col]):
            total_sold = df[sold_col].sum()
            
            if total_sold > 0:
                turnover = total_sold / avg_inventory
                days_inventory = 365 / turnover if turnover > 0 else 0
                
                kpis.append(safe_kpi(
                    category="📦 Inventory",
                    name="Inventory Turnover Ratio",
                    value=f"{turnover:.2f}x",
                    formula="Total Units Sold / Avg Inventory",
                    source=f"`{sold_col}`, `{inventory_col}`",
                    confidence=conf,
                    warnings="Low turnover - Excess inventory" if turnover < 2 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="📦 Inventory",
                    name="Days Inventory Outstanding (DIO)",
                    value=f"{days_inventory:.1f} days",
                    formula="365 / Turnover Ratio",
                    source=f"`{sold_col}`, `{inventory_col}`",
                    confidence=conf,
                    warnings=warns
                ))
    
    # Dead stock analysis
    if sold_col and pd.api.types.is_numeric_dtype(df[sold_col]):
        inventory_items = (df[inventory_col].fillna(0) > 0).sum()
        unsold_items = (df[sold_col].fillna(0) <= 0).sum()
        dead_stock_pct = (unsold_items / inventory_items * 100) if inventory_items > 0 else 0
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Dead Stock %",
            value=f"{dead_stock_pct:.2f}%",
            formula="(Items in stock but not sold / Total in-stock) * 100",
            source=f"`{inventory_col}`, `{sold_col}`",
            confidence=conf,
            warnings="High dead stock - Review SKUs" if dead_stock_pct > 20 else warns
        ))
    
    # Stockout frequency
    if stockout_col:
        stockout_mask = df[stockout_col].astype(str).str.lower().isin(['true', '1', 'yes', 'y'])
        stockout_freq = (stockout_mask.sum() / len(df) * 100) if len(df) > 0 else 0
    else:
        # Infer stockouts from zero inventory
        stockout_freq = (valid_inventory <= 0).sum() / len(valid_inventory) * 100 if len(valid_inventory) > 0 else 0
    
    kpis.append(safe_kpi(
        category="📦 Inventory",
        name="Stockout Frequency",
        value=f"{stockout_freq:.2f}%",
        formula="Stockout Events / Total Observations * 100",
        source=f"`{stockout_col if stockout_col else inventory_col}`",
        confidence=conf,
        warnings="High stockout rate - Stock out more" if stockout_freq > 10 else warns
    ))
    
    # Sell-through rate
    if sold_col and received_col and pd.api.types.is_numeric_dtype(df[sold_col]) and pd.api.types.is_numeric_dtype(df[received_col]):
        received_total = df[received_col].sum()
        sold_total = df[sold_col].sum()
        
        sell_through = (sold_total / received_total * 100) if received_total > 0 else 0
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Sell-Through Rate",
            value=f"{sell_through:.2f}%",
            formula="(Units Sold / Units Received) * 100",
            source=f"`{sold_col}`, `{received_col}`",
            confidence=conf,
            warnings="Low sell-through - Inventory buildup" if sell_through < 50 else warns
        ))
    
    return kpis
