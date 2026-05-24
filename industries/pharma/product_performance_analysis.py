"""
Product sales performance, market share, and lifecycle metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_product_performance_metrics(df):
    """Calculates product performance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Product metrics are COUNT (units) or MONEY (revenue), not time
    product_col = first_column(df, ["product_id", "drug_name", "product", "formulation"])
    sales_col = first_column(df, ["sales_volume", "units_sold", "sales_units"])
    revenue_col = first_column(df, ["revenue", "sales_revenue", "total_revenue"])
    growth_col = first_column(df, ["growth_rate", "yoy_growth", "growth_pct"])
    market_share_col = first_column(df, ["market_share", "market_share_pct", "share"])
    
    if not product_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [product_col, sales_col, revenue_col, growth_col, market_share_col] if col])
    
    # Total products
    total_products = df[product_col].nunique()
    
    kpis.append(safe_kpi(
        category="💊 Product Performance",
        name="Total Products",
        value=f"{total_products:,}",
        formula="Count(Distinct Products)",
        source=f"`{product_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Product sales
    if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        total_sales = df[sales_col].sum()
        product_sales = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False)
        
        kpis.append(safe_kpi(
            category="💊 Product Performance",
            name="Total Product Sales",
            value=f"{total_sales:,.0f} units",
            formula="Sum(Units Sold)",
            source=f"`{sales_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        if not product_sales.empty:
            # Top 3 products
            top_3 = product_sales.head(3)
            top_3_sales = top_3.sum()
            top_3_pct = (top_3_sales / total_sales * 100) if total_sales > 0 else 0
            
            kpis.append(safe_kpi(
                category="💊 Product Performance",
                name="Top 3 Products Market Share",
                value=f"{top_3_pct:.2f}%",
                formula="(Top 3 Total / Total) * 100",
                source=f"`{product_col}`, `{sales_col}`",
                confidence=conf,
                warnings="High concentration in top 3" if top_3_pct > 60 else warns
            ))
    
    # Product revenue
    if revenue_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_revenue = df[revenue_col].sum()
        product_revenue = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
        
        kpis.append(safe_kpi(
            category="💊 Product Performance",
            name="Total Product Revenue",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        if not product_revenue.empty:
            revenue_per_unit = total_revenue / (df[sales_col].sum() if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]) else 1)
            
            kpis.append(safe_kpi(
                category="💊 Product Performance",
                name="Avg Revenue per Unit",
                value=f"${revenue_per_unit:,.2f}",
                formula="Total Revenue / Total Units",
                source=f"`{revenue_col}`, `{sales_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Growth metrics
    if growth_col and pd.api.types.is_numeric_dtype(df[growth_col]):
        valid_growth = df[growth_col].dropna()
        
        if not valid_growth.empty:
            avg_growth = valid_growth.mean()
            
            kpis.append(safe_kpi(
                category="💊 Product Performance",
                name="Avg Product Growth Rate",
                value=f"{avg_growth:.2f}%",
                formula="Mean(Growth %)",
                source=f"`{growth_col}`",
                confidence=conf,
                warnings="Negative growth - Declining product" if avg_growth < 0 else "Low growth" if avg_growth < 5 else warns
            ))
    
    # Market share
    if market_share_col and pd.api.types.is_numeric_dtype(df[market_share_col]):
        valid_share = df[market_share_col].dropna()
        
        if not valid_share.empty:
            avg_market_share = valid_share.mean()
            max_market_share = valid_share.max()
            
            kpis.append(safe_kpi(
                category="💊 Product Performance",
                name="Avg Market Share",
                value=f"{avg_market_share:.2f}%",
                formula="Mean(Market Share)",
                source=f"`{market_share_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💊 Product Performance",
                name="Max Market Share (Leading Product)",
                value=f"{max_market_share:.2f}%",
                formula="Max(Market Share)",
                source=f"`{market_share_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
