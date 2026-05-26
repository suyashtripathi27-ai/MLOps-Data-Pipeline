"""
Pricing strategy, discounts, and margin analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_pricing_metrics(df, enable_debug=False):
    """
    Calculate pricing and margin KPIs with optional execution tracing.
    
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
    
    regular_price_col, regular_price_series = engine.get_numeric(["regular_price", "list_price", "base_price", "msrp"])
    selling_price_col, selling_price_series = engine.get_numeric(["selling_price", "sale_price", "price", "final_price"])
    discount_col, discount_series = engine.get_numeric(["discount", "discount_amount", "discount_pct", "discount_percentage"])
    cost_col, cost_series = engine.get_numeric(["cost", "cogs", "unit_cost", "manufacturing_cost"])
    
    if selling_price_col is not None:
        avg_price = selling_price_series.mean()
        median_price = selling_price_series.median()
        
        kpis.append(engine.build_kpi(
            category="💰 Pricing", name="Avg Selling Price",
            value=f"${avg_price:,.2f}", formula="Mean(Selling Price)", source=f"`{selling_price_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="💰 Pricing", name="Median Selling Price",
            value=f"${median_price:,.2f}", formula="Median(Selling Price)", source=f"`{selling_price_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💰 Pricing", "Selling Price", "Missing numeric 'selling_price'."))
    
    # Discount analysis
    if discount_col is not None:
        avg_discount = discount_series.mean()
        discount_items = (discount_series > 0).sum()
        discount_rate = (discount_items / len(df) * 100) if len(df) > 0 else 0
        warn_msg = "High discount rate" if discount_rate > 50 else "None"
        
        kpis.append(engine.build_kpi(
            category="💰 Pricing", name="Avg Discount",
            value=f"${avg_discount:,.2f}" if discount_series.max() > 100 else f"{avg_discount:.2f}%",
            formula="Mean(Discount)", source=f"`{discount_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="💰 Pricing", name="Discounted Items %",
            value=f"{discount_rate:.2f}%", formula="(Items with Discount / Total) * 100", source=f"`{discount_col}`",
            warnings=warn_msg
        ))
    
    # Margin analysis
    if cost_col is not None and selling_price_col is not None:
        margin_df = pd.DataFrame({"cost": cost_series, "price": selling_price_series}).dropna()
        
        if len(margin_df) > 0:
            margin_df["margin"] = (margin_df["price"] - margin_df["cost"]) / (margin_df["price"] + 0.0001) * 100
            valid_margins = margin_df[margin_df["margin"] >= 0]["margin"]
            
            if len(valid_margins) > 0:
                avg_margin = valid_margins.mean()
                warn_msg = "Low margin" if avg_margin < 20 else "None"
                
                kpis.append(engine.build_kpi(
                    category="💰 Pricing", name="Avg Profit Margin %",
                    value=f"{avg_margin:.2f}%", formula="Mean((Price - Cost) / Price * 100)", source=f"`{cost_col}`, `{selling_price_col}`",
                    warnings=warn_msg
                ))
    
    # Price elasticity
    if regular_price_col is not None and selling_price_col is not None:
        price_df = pd.DataFrame({"regular": regular_price_series, "selling": selling_price_series}).dropna()
        
        if len(price_df) > 0 and (price_df["regular"] > 0).all():
            discount_factor = (price_df["regular"] - price_df["selling"]) / price_df["regular"]
            avg_discount_factor = discount_factor.mean() * 100
            
            kpis.append(engine.build_kpi(
                category="💰 Pricing", name="Avg Discount from List Price",
                value=f"{avg_discount_factor:.2f}%", formula="Mean((List - Sell) / List * 100)", source=f"`{regular_price_col}`, `{selling_price_col}`"
            ))
    
    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
