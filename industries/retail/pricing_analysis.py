"""
Pricing strategy, discounts, margins, and price elasticity metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_pricing_metrics(df):
    """Calculates pricing and margin KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Pricing metrics are MONEY, not time
    regular_price_col = first_column(df, ["regular_price", "list_price", "base_price", "msrp"])
    selling_price_col = first_column(df, ["selling_price", "sale_price", "price", "final_price"])
    discount_col = first_column(df, ["discount", "discount_amount", "discount_pct", "discount_percentage"])
    cost_col = first_column(df, ["cost", "cogs", "unit_cost"])
    quantity_col = first_column(df, ["quantity", "units_sold", "qty"])
    
    if not selling_price_col:
        return kpis
    
    # Price is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[selling_price_col]):
        kpis.append(safe_kpi(
            category="💰 Pricing",
            name="Pricing Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{selling_price_col}`",
            confidence="Low",
            warnings="Price column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [regular_price_col, selling_price_col, discount_col, cost_col, quantity_col] if col])
    
    # Price metrics
    valid_price = df[selling_price_col].dropna()
    
    if not valid_price.empty:
        avg_price = valid_price.mean()
        median_price = valid_price.median()
        
        kpis.append(safe_kpi(
            category="💰 Pricing",
            name="Avg Selling Price",
            value=f"${avg_price:,.2f}",
            formula="Mean(Selling Price)",
            source=f"`{selling_price_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Pricing",
            name="Median Selling Price",
            value=f"${median_price:,.2f}",
            formula="Median(Selling Price)",
            source=f"`{selling_price_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Discount analysis
    if discount_col and pd.api.types.is_numeric_dtype(df[discount_col]):
        valid_discount = df[discount_col].dropna()
        
        if not valid_discount.empty:
            avg_discount = valid_discount.mean()
            discounted_items = (valid_discount > 0).sum()
            discount_rate = (discounted_items / len(df) * 100) if len(df) > 0 else 0
            
            kpis.append(safe_kpi(
                category="💰 Pricing",
                name="Avg Discount Amount",
                value=f"${avg_discount:,.2f}",
                formula="Mean(Discount)",
                source=f"`{discount_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💰 Pricing",
                name="Discounted Items %",
                value=f"{discount_rate:.2f}%",
                formula="(Items with Discount / Total) * 100",
                source=f"`{discount_col}`",
                confidence=conf,
                warnings="High discount rate - Margin pressure" if discount_rate > 50 else warns
            ))
    
    # Margin analysis
    if cost_col and selling_price_col and pd.api.types.is_numeric_dtype(df[cost_col]) and pd.api.types.is_numeric_dtype(df[selling_price_col]):
        margin_df = pd.DataFrame({
            "cost": df[cost_col],
            "price": df[selling_price_col]
        }).dropna()
        
        if not margin_df.empty:
            margin_df["margin"] = ((margin_df["price"] - margin_df["cost"]) / margin_df["price"] * 100)
            valid_margins = margin_df[margin_df["margin"] >= 0]["margin"]
            
            if not valid_margins.empty:
                avg_margin = valid_margins.mean()
                
                kpis.append(safe_kpi(
                    category="💰 Pricing",
                    name="Avg Profit Margin %",
                    value=f"{avg_margin:.2f}%",
                    formula="Mean((Price - Cost) / Price * 100)",
                    source=f"`{selling_price_col}`, `{cost_col}`",
                    confidence=conf,
                    warnings="Low margin" if avg_margin < 20 else warns
                ))
    
    # Price elasticity
    if regular_price_col and selling_price_col and quantity_col and pd.api.types.is_numeric_dtype(df[regular_price_col]) and pd.api.types.is_numeric_dtype(df[selling_price_col]) and pd.api.types.is_numeric_dtype(df[quantity_col]):
        price_df = pd.DataFrame({
            "regular": df[regular_price_col],
            "selling": df[selling_price_col],
            "qty": df[quantity_col]
        }).dropna()
        
        if not price_df.empty and (price_df["regular"] > 0).all():
            discount_factor = (price_df["regular"] - price_df["selling"]) / price_df["regular"]
            avg_discount_factor = discount_factor.mean() * 100
            
            kpis.append(safe_kpi(
                category="💰 Pricing",
                name="Avg Discount from List Price",
                value=f"{avg_discount_factor:.2f}%",
                formula="Mean((List - Sell) / List * 100)",
                source=f"`{regular_price_col}`, `{selling_price_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
