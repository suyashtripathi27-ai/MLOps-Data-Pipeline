import pandas as pd
from utils.validator import SemanticValidator
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_inventory_metrics(df):
    kpis = []
    inventory_col = first_column(df, ["inventory_level", "stock_level", "on_hand_inventory", "on_hand"])
    sold_col = first_column(df, ["units_sold", "quantity_sold", "sales_units", "units_ordered"])
    received_col = first_column(df, ["units_received", "quantity_received", "units_purchased", "replenished_units"])
    cogs_col = first_column(df, ["cogs", "cost_of_goods_sold", "cost"])
    stockout_col = first_column(df, ["stockout_flag", "is_stockout", "out_of_stock"])
    if not inventory_col:
        return kpis

    inv_valid, reason = SemanticValidator.is_valid_duration(df[inventory_col])
    if not inv_valid:
        return [safe_kpi("📦 Inventory Analysis", "Inventory Metrics", "EXCLUDED", "N/A", f"`{inventory_col}`", "Low", reason)]

    conf, warns = confidence_for(df, [inventory_col, sold_col, received_col, cogs_col, stockout_col])
    avg_inventory = df[inventory_col].dropna().mean()
    if avg_inventory and avg_inventory > 0 and sold_col and df[sold_col].fillna(0).sum() > 0:
        turnover = df[sold_col].fillna(0).sum() / avg_inventory
        days_inventory = 365 / turnover if turnover > 0 else 0
        kpis.append(safe_kpi("📦 Inventory Analysis", "Inventory Turnover Ratio", f"{turnover:.2f}", "Total Units Sold / Avg Inventory", f"`{sold_col}`, `{inventory_col}`", conf, warns))
        kpis.append(safe_kpi("📦 Inventory Analysis", "Days of Inventory", f"{days_inventory:.1f} days", "365 / Inventory Turnover", f"`{sold_col}`, `{inventory_col}`", conf, warns))

    if sold_col:
        zero_sales_ratio = (df[sold_col].fillna(0) <= 0).mean() * 100
        kpis.append(safe_kpi("📦 Inventory Analysis", "Zero-Sales Item Rate", f"{zero_sales_ratio:.2f}%", "Rows with zero sold units / Total rows * 100", f"`{sold_col}`", conf, warns))

    if inventory_col:
        in_stock = df[inventory_col].fillna(0) > 0
        dead_stock = in_stock.sum()
        dead_stock_pct = ((df[sold_col].fillna(0) <= 0).sum() / dead_stock * 100) if sold_col and dead_stock > 0 else 0
        kpis.append(safe_kpi("📦 Inventory Analysis", "Dead Stock %", f"{dead_stock_pct:.2f}%", "Items with inventory but no sales / In-stock items * 100", f"`{inventory_col}`" + (f", `{sold_col}`" if sold_col else ""), conf, warns))

    if stockout_col:
        stockout_series = df[stockout_col].astype(str).str.lower().isin(["true", "1", "yes", "y"])
        stockout_freq = stockout_series.mean() * 100
    else:
        stockout_freq = (df[inventory_col].fillna(0) <= 0).mean() * 100
    kpis.append(safe_kpi("📦 Inventory Analysis", "Stockout Frequency", f"{stockout_freq:.2f}%", "Stockout events / Total observations * 100", f"`{stockout_col}`" if stockout_col else f"`{inventory_col}`", conf, warns))

    if sold_col and received_col:
        received_total = df[received_col].fillna(0).sum()
        sell_through = (df[sold_col].fillna(0).sum() / received_total) * 100 if received_total > 0 else 0
        kpis.append(safe_kpi("📦 Inventory Analysis", "Sell-Through Rate", f"{sell_through:.2f}%", "Units Sold / Units Received * 100", f"`{sold_col}`, `{received_col}`", conf, warns))
    elif cogs_col and avg_inventory > 0:
        turnover = df[cogs_col].fillna(0).sum() / avg_inventory
        kpis.append(safe_kpi("📦 Inventory Analysis", "COGS Turnover Ratio", f"{turnover:.2f}", "COGS / Avg Inventory", f"`{cogs_col}`, `{inventory_col}`", conf, warns))

    return kpis
