"""
Inventory turnover, stock levels, dead stock, and stockout metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_inventory_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    inv_col, inv_series = engine.get_numeric(["inventory_level", "stock_level", "on_hand_inventory", "stock_on_hand"])
    sold_col, sold_series = engine.get_numeric(["units_sold", "quantity_sold", "sales_units"])
    received_col, received_series = engine.get_numeric(["units_received", "quantity_received", "stock_received"])
    stockout_col, stockout_series = engine.get_column(["stockout_flag", "is_stockout", "out_of_stock"])
    
    if inv_col is not None:
        inv_clean = inv_series.dropna()
        if len(inv_clean) > 0:
            avg_inv = inv_clean.mean()
            kpis.append(engine.build_kpi("📦 Inventory", "Total Inventory Units", f"{inv_clean.sum():,.0f}", "Sum(Inventory)", f"`{inv_col}`"))
            kpis.append(engine.build_kpi("📦 Inventory", "Avg Inventory Level", f"{avg_inv:,.0f}", "Mean(Inventory)", f"`{inv_col}`"))
            
            if sold_col is not None:
                turnover_df = pd.concat([inv_series, sold_series], axis=1).dropna()
                if len(turnover_df) > 0:
                    total_sold = turnover_df[sold_col].sum()
                    avg_inventory_valid = turnover_df[inv_col].mean()
                    
                    if avg_inventory_valid > 0:
                        turnover = total_sold / avg_inventory_valid
                        dio = 365 / turnover if turnover > 0 else 0
                        kpis.append(engine.build_kpi("📦 Inventory", "Inventory Turnover Ratio", f"{turnover:.2f}x", "Sold / Avg Inventory", f"`{sold_col}`, `{inv_col}`", warnings="Low turnover" if turnover < 2 else "None"))
                        kpis.append(engine.build_kpi("📦 Inventory", "Days Inventory Outstanding (DIO)", f"{dio:.1f} days", "365 / Turnover", f"`{sold_col}`, `{inv_col}`"))
                    
                    inv_items = (turnover_df[inv_col] > 0).sum()
                    unsold = (turnover_df[sold_col] <= 0).sum()
                    dead_pct = (unsold / inv_items * 100) if inv_items > 0 else 0
                    kpis.append(engine.build_kpi("📦 Inventory", "Dead Stock %", f"{dead_pct:.2f}%", "(Unsold / In-Stock) * 100", f"`{inv_col}`, `{sold_col}`", warnings="High dead stock" if dead_pct > 20 else "None"))
        else:
            kpis.append(engine.log_missing("📦 Inventory", "Levels", "All inventory data is null."))
    else:
        kpis.append(engine.log_missing("📦 Inventory", "Levels", "Missing numeric 'inventory_level'."))

    if stockout_col is not None:
        stockout_clean = stockout_series.dropna().astype(str).str.lower()
        if len(stockout_clean) > 0:
            stockouts = stockout_clean.isin(['true', '1', 'yes', 'y']).sum()
            stockout_freq = (stockouts / len(stockout_clean) * 100)
            kpis.append(engine.build_kpi("📦 Inventory", "Stockout Frequency", f"{stockout_freq:.2f}%", "Stockouts / Total * 100", f"`{stockout_col}`", warnings="High stockout rate" if stockout_freq > 10 else "None"))
    elif inv_col is not None and len(inv_clean) > 0:
        stockout_freq = (inv_clean <= 0).sum() / len(inv_clean) * 100
        kpis.append(engine.build_kpi("📦 Inventory", "Stockout Frequency (Inferred)", f"{stockout_freq:.2f}%", "Zero Inventory / Total * 100", f"`{inv_col}`", warnings="High stockout rate" if stockout_freq > 10 else "None"))

    if sold_col is not None and received_col is not None:
        st_df = pd.concat([sold_series, received_series], axis=1).dropna()
        if len(st_df) > 0:
            total_rec = st_df[received_col].sum()
            total_sold = st_df[sold_col].sum()
            sell_through = (total_sold / total_rec * 100) if total_rec > 0 else 0
            kpis.append(engine.build_kpi("📦 Inventory", "Sell-Through Rate", f"{sell_through:.2f}%", "(Sold / Received) * 100", f"`{sold_col}`, `{received_col}`", warnings="Low sell-through" if sell_through < 50 else "None"))

    if enable_debug: engine.print_execution_log()
    return kpis
