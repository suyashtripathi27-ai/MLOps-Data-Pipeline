"""
Pricing strategy, discounts, margins, and price elasticity metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_pricing_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    reg_price_col, reg_price_series = engine.get_numeric(["regular_price", "list_price", "base_price", "msrp"])
    sell_price_col, sell_price_series = engine.get_numeric(["selling_price", "sale_price", "price", "final_price"])
    discount_col, discount_series = engine.get_numeric(["discount", "discount_amount", "discount_pct", "discount_percentage"])
    cost_col, cost_series = engine.get_numeric(["cost", "cogs", "unit_cost"])
    
    if sell_price_col is not None:
        price_clean = sell_price_series.dropna()
        if len(price_clean) > 0:
            kpis.append(engine.build_kpi("💰 Pricing", "Avg Selling Price", f"${price_clean.mean():,.2f}", "Mean(Selling Price)", f"`{sell_price_col}`"))
            kpis.append(engine.build_kpi("💰 Pricing", "Median Selling Price", f"${price_clean.median():,.2f}", "Median(Selling Price)", f"`{sell_price_col}`"))
    else:
        kpis.append(engine.log_missing("💰 Pricing", "Prices", "Missing numeric 'selling_price'."))

    if discount_col is not None:
        disc_clean = discount_series.dropna()
        if len(disc_clean) > 0:
            avg_disc = disc_clean.mean()
            disc_rate = (disc_clean > 0).sum() / len(df) * 100
            kpis.append(engine.build_kpi("💰 Pricing", "Avg Discount Amount", f"${avg_disc:,.2f}", "Mean(Discount)", f"`{discount_col}`"))
            kpis.append(engine.build_kpi("💰 Pricing", "Discounted Items %", f"{disc_rate:.2f}%", "(Items with Discount / Total) * 100", f"`{discount_col}`", warnings="High discount rate" if disc_rate > 50 else "None"))
    else:
        kpis.append(engine.log_missing("💰 Pricing", "Discounts", "Missing numeric 'discount'."))

    if cost_col is not None and sell_price_col is not None:
        margin_df = pd.concat([cost_series, sell_price_series], axis=1).dropna()
        if len(margin_df) > 0:
            margin_df["margin"] = ((margin_df[sell_price_col] - margin_df[cost_col]) / margin_df[sell_price_col] * 100)
            valid_margins = margin_df[margin_df["margin"] >= 0]["margin"]
            if len(valid_margins) > 0:
                avg_margin = valid_margins.mean()
                kpis.append(engine.build_kpi("💰 Pricing", "Avg Profit Margin %", f"{avg_margin:.2f}%", "Mean((Price - Cost) / Price * 100)", f"`{sell_price_col}`, `{cost_col}`", warnings="Low margin" if avg_margin < 20 else "None"))
    
    if reg_price_col is not None and sell_price_col is not None:
        elast_df = pd.concat([reg_price_series, sell_price_series], axis=1).dropna()
        if len(elast_df) > 0 and (elast_df[reg_price_col] > 0).all():
            disc_factor = ((elast_df[reg_price_col] - elast_df[sell_price_col]) / elast_df[reg_price_col]).mean() * 100
            kpis.append(engine.build_kpi("💰 Pricing", "Avg Discount from List Price", f"{disc_factor:.2f}%", "Mean((List - Sell) / List * 100)", f"`{reg_price_col}`, `{sell_price_col}`"))

    if enable_debug: engine.print_execution_log()
    return kpis
