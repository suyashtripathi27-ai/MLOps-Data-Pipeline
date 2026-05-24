"""
Product performance, category analysis, and top performers.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_product_metrics(df):
    """Calculates product performance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    product_col = first_column(df, ["product_id", "product_name", "sku", "product_key"])
    category_col = first_column(df, ["category", "product_category", "category_id", "dept"])
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "product_revenue"])
    quantity_col = first_column(df, ["quantity", "units_sold", "sales_qty"])
    rating_col = first_column(df, ["rating", "product_rating", "avg_rating", "score"])
    
    if not product_col or not revenue_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [product_col, category_col, revenue_col, quantity_col, rating_col] if col])
    
    # Total products
    total_products = df[product_col].nunique()
    
    kpis.append(safe_kpi(
        category="🏷️ Product Analysis",
        name="Total Unique Products",
        value=f"{total_products:,}",
        formula="Count(Distinct Products)",
        source=f"`{product_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Revenue by product
    if pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_revenue = df[revenue_col].sum()
        product_revenue = df.groupby(product_col)[revenue_col].sum().sort_values(ascending=False)
        
        kpis.append(safe_kpi(
            category="🏷️ Product Analysis",
            name="Total Product Revenue",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        if not product_revenue.empty:
            top_product = product_revenue.idxmax()
            top_product_rev = product_revenue.max()
            top_product_share = (top_product_rev / total_revenue * 100) if total_revenue > 0 else 0
            
            kpis.append(safe_kpi(
                category="🏷️ Product Analysis",
                name="Top Performing Product",
                value=f"{top_product} (${top_product_rev:,.2f})",
                formula="Product with max revenue",
                source=f"`{product_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🏷️ Product Analysis",
                name="Top Product Revenue Share",
                value=f"{top_product_share:.2f}%",
                formula="Top Product / Total Revenue * 100",
                source=f"`{product_col}`, `{revenue_col}`",
                confidence=conf,
                warnings="High concentration" if top_product_share > 20 else warns
            ))
    
    # Category analysis
    if category_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        category_revenue = df.groupby(category_col)[revenue_col].sum().sort_values(ascending=False)
        
        if not category_revenue.empty:
            total_cats = len(category_revenue)
            top_cat = category_revenue.idxmax()
            
            kpis.append(safe_kpi(
                category="🏷️ Product Analysis",
                name="Total Categories",
                value=f"{total_cats}",
                formula="Count(Distinct Categories)",
                source=f"`{category_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🏷️ Product Analysis",
                name="Top Category",
                value=f"{top_cat} (${category_revenue.max():,.2f})",
                formula="Category with max revenue",
                source=f"`{category_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Rating analysis
    if rating_col and pd.api.types.is_numeric_dtype(df[rating_col]):
        valid_rating = df[rating_col].dropna()
        
        if not valid_rating.empty:
            avg_rating = valid_rating.mean()
            median_rating = valid_rating.median()
            
            kpis.append(safe_kpi(
                category="🏷️ Product Analysis",
                name="Avg Product Rating",
                value=f"{avg_rating:.2f}/5.0",
                formula="Mean(Rating)",
                source=f"`{rating_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🏷️ Product Analysis",
                name="Median Product Rating",
                value=f"{median_rating:.2f}/5.0",
                formula="Median(Rating)",
                source=f"`{rating_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Units sold
    if quantity_col and pd.api.types.is_numeric_dtype(df[quantity_col]):
        total_units = df[quantity_col].sum()
        avg_units_per_product = df.groupby(product_col)[quantity_col].sum().mean()
        
        kpis.append(safe_kpi(
            category="🏷️ Product Analysis",
            name="Total Units Sold",
            value=f"{total_units:,.0f}",
            formula="Sum(Quantity)",
            source=f"`{quantity_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🏷️ Product Analysis",
            name="Avg Units per Product",
            value=f"{avg_units_per_product:,.0f}",
            formula="Mean(Product Units)",
            source=f"`{quantity_col}`, `{product_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
