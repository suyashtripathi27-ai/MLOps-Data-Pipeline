"""
Product performance, category analysis, and top performers.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_product_metrics(df, enable_debug=False):
    """
    Calculate product performance KPIs with optional execution tracing.
    
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
    
    product_col, product_series = engine.get_column(["product_id", "product_name", "sku", "product_key"])
    category_col, category_series = engine.get_column(["category", "product_category", "category_id", "dept"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "order_value", "product_revenue"])
    quantity_col, quantity_series = engine.get_numeric(["quantity", "units_sold", "sales_qty"])
    rating_col, rating_series = engine.get_numeric(["rating", "product_rating", "avg_rating", "score"])
    
    if product_col is not None:
        total_products = product_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="🧸 Product Analysis", name="Total Unique Products",
            value=f"{total_products:,}", formula="Count(Distinct Products)", source=f"`{product_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🧸 Product Analysis", "Product Count", "Missing 'product_id'."))
    
    # Revenue by product
    if revenue_col is not None and product_col is not None:
        total_revenue = revenue_series.sum()
        product_revenue = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
        
        kpis.append(engine.build_kpi(
            category="🧸 Product Analysis", name="Total Product Revenue",
            value=f"${total_revenue:,.2f}", formula="Sum(Revenue)", source=f"`{revenue_col}`"
        ))
        
        if len(product_revenue) > 0:
            top_product = product_revenue.idxmax()
            top_product_rev = product_revenue.max()
            top_product_share = (top_product_rev / total_revenue * 100) if total_revenue > 0 else 0
            warn_msg = "High concentration" if top_product_share > 20 else "None"
            
            kpis.append(engine.build_kpi(
                category="🧸 Product Analysis", name="Top Performing Product",
                value=f"{top_product} (${top_product_rev:,.2f})", formula="Product with max revenue", source=f"`{product_col}`, `{revenue_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="🧸 Product Analysis", name="Top Product Revenue Share",
                value=f"{top_product_share:.2f}%", formula="Top Product / Total Revenue * 100", source=f"`{product_col}`, `{revenue_col}`",
                warnings=warn_msg
            ))
    
    # Category analysis
    if category_col is not None and revenue_col is not None:
        category_revenue = df.groupby(category_col)[revenue_col].sum().sort_values(ascending=False)
        
        if len(category_revenue) > 0:
            total_cats = len(category_revenue)
            top_cat = category_revenue.idxmax()
            
            kpis.append(engine.build_kpi(
                category="🧸 Product Analysis", name="Total Categories",
                value=f"{total_cats}", formula="Count(Distinct Categories)", source=f"`{category_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="🧸 Product Analysis", name="Top Category",
                value=f"{top_cat} (${category_revenue.max():,.2f})", formula="Category with max revenue", source=f"`{category_col}`, `{revenue_col}`"
            ))
    
    # Rating analysis
    if rating_col is not None:
        avg_rating = rating_series.mean()
        median_rating = rating_series.median()
        
        kpis.append(engine.build_kpi(
            category="🧸 Product Analysis", name="Avg Product Rating",
            value=f"{avg_rating:.2f}/5.0", formula="Mean(Rating)", source=f"`{rating_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="🧸 Product Analysis", name="Median Product Rating",
            value=f"{median_rating:.2f}/5.0", formula="Median(Rating)", source=f"`{rating_col}`"
        ))
    
    # Units sold
    if quantity_col is not None and product_col is not None:
        total_units = quantity_series.sum()
        avg_units_per_product = df.groupby(product_col)[quantity_col].sum().mean()
        
        kpis.append(engine.build_kpi(
            category="🧸 Product Analysis", name="Total Units Sold",
            value=f"{total_units:,.0f}", formula="Sum(Quantity)", source=f"`{quantity_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="🧸 Product Analysis", name="Avg Units per Product",
            value=f"{avg_units_per_product:,.0f}", formula="Mean(Product Units)", source=f"`{quantity_col}`, `{product_col}`"
        ))

    if enable_debug:
        engine.print_execution_log()
    
    return kpis
