import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_inventory_metrics(df):
    """Calculates inventory turnover, stock risk, and replenishment KPIs."""
    kpis = []
    inventory_col = _first_column(df, ["inventory_level", "stock_level", "on_hand_inventory", "on_hand"])
    sold_col = _first_column(df, ["units_sold", "quantity_sold", "sales_units"])
    received_col = _first_column(df, ["units_received", "quantity_received", "units_purchased"])
    cogs_col = _first_column(df, ["cogs", "cost_of_goods_sold", "cost"])
    stockout_col = _first_column(df, ["stockout_flag", "is_stockout"])

    if not inventory_col:
        return kpis

    inv_valid, inv_reason = SemanticValidator.is_valid_duration(df[inventory_col])
    if not inv_valid:
        kpis.append({
            "category": "📦 Inventory Analysis",
            "name": "Inventory Metrics",
            "value": "EXCLUDED",
            "formula": "N/A",
            "source": f"`{inventory_col}`",
            "confidence": "Low",
            "warnings": inv_reason,
        })
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [inventory_col, sold_col] if sold_col else [inventory_col])
    avg_inventory = df[inventory_col].dropna().mean()
    if avg_inventory and avg_inventory > 0:
        if sold_col and df[sold_col].sum() > 0:
            turnover = df[sold_col].sum() / avg_inventory
            days_inventory = 365 / turnover if turnover > 0 else 0
            kpis.append({
                "category": "📦 Inventory Analysis",
                "name": "Inventory Turnover Ratio",
                "value": f"{turnover:.2f}",
                "formula": "Total Units Sold / Avg Inventory",
                "source": f"`{sold_col}`, `{inventory_col}`",
                "confidence": conf,
                "warnings": warns,
            })
            kpis.append({
                "category": "📦 Inventory Analysis",
                "name": "Days of Inventory",
                "value": f"{days_inventory:.1f} days",
                "formula": "365 / Inventory Turnover",
                "source": f"`{sold_col}`, `{inventory_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    dead_stock = (df[inventory_col].fillna(0) > 0).sum()
    sold_ratio = 0
    if sold_col:
        sold_ratio = (df[sold_col].fillna(0) <= 0).sum()
    dead_stock_pct = (sold_ratio / dead_stock) * 100 if dead_stock > 0 else 0
    kpis.append({
        "category": "📦 Inventory Analysis",
        "name": "Dead Stock %",
        "value": f"{dead_stock_pct:.2f}%",
        "formula": "Items with inventory but zero sales / In-stock items * 100",
        "source": f"`{inventory_col}`" + (f", `{sold_col}`" if sold_col else ""),
        "confidence": conf,
        "warnings": warns,
    })

    if stockout_col:
        stockout_series = df[stockout_col].astype(str).str.lower().isin(["true", "1", "yes", "y"])
        stockout_freq = stockout_series.mean() * 100
    else:
        stockout_freq = (df[inventory_col].fillna(0) <= 0).mean() * 100
    kpis.append({
        "category": "📦 Inventory Analysis",
        "name": "Stockout Frequency",
        "value": f"{stockout_freq:.2f}%",
        "formula": "Stockout events / Total observations * 100",
        "source": f"`{stockout_col}`" if stockout_col else f"`{inventory_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if sold_col and received_col:
        received_total = df[received_col].fillna(0).sum()
        sell_through = (df[sold_col].fillna(0).sum() / received_total) * 100 if received_total > 0 else 0
        kpis.append({
            "category": "📦 Inventory Analysis",
            "name": "Sell-Through Rate",
            "value": f"{sell_through:.2f}%",
            "formula": "Units Sold / Units Received * 100",
            "source": f"`{sold_col}`, `{received_col}`",
            "confidence": conf,
            "warnings": warns,
        })
    elif cogs_col and avg_inventory > 0:
        turnover = df[cogs_col].fillna(0).sum() / avg_inventory
        kpis.append({
            "category": "📦 Inventory Analysis",
            "name": "Inventory Turnover Ratio",
            "value": f"{turnover:.2f}",
            "formula": "COGS / Avg Inventory",
            "source": f"`{cogs_col}`, `{inventory_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    return kpis
