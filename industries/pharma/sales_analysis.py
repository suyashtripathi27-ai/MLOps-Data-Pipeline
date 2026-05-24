"""
Pharmaceutical sales, product performance, and market metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_pharma_sales_metrics(df):
    """Calculates pharmaceutical sales and market KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Sales are COUNT (units) or MONEY (revenue), not time
    sales_col = first_column(df, ["sales_volume", "units_sold", "sales_units", "quantity_sold"])
    revenue_col = first_column(df, ["revenue", "sales_revenue", "total_sales", "gross_revenue"])
    product_col = first_column(df, ["product_id", "drug_name", "product", "formulation"])
    region_col = first_column(df, ["region", "territory", "market"])
    class_col = first_column(df, ["drug_class", "therapeutic_class", "ata_code"])
    
    if not sales_col and not revenue_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [sales_col, revenue_col, product_col, region_col, class_col] if col])
    
    # Total sales volume
    if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        total_units = df[sales_col].sum()
        avg_units = df[sales_col].mean()
        
        kpis.append(safe_kpi(
            category="💊 Pharma Sales",
            name="Total Units Sold",
            value=f"{total_units:,.0f}",
            formula="Sum(Sales Volume)",
            source=f"`{sales_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💊 Pharma Sales",
            name="Avg Units Sold (per Period/Record)",
            value=f"{avg_units:,.0f}",
            formula="Mean(Sales Volume)",
            source=f"`{sales_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Revenue
    if revenue_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_revenue = df[revenue_col].sum()
        avg_revenue = df[revenue_col].mean()
        
        kpis.append(safe_kpi(
            category="💊 Pharma Sales",
            name="Total Sales Revenue",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💊 Pharma Sales",
            name="Avg Revenue (per Record)",
            value=f"${avg_revenue:,.2f}",
            formula="Mean(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Price per unit
    if sales_col and revenue_col and pd.api.types.is_numeric_dtype(df[sales_col]) and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_units = df[sales_col].sum()
        total_revenue = df[revenue_col].sum()
        
        if total_units > 0:
            price_per_unit = total_revenue / total_units
            
            kpis.append(safe_kpi(
                category="💊 Pharma Sales",
                name="Avg Price per Unit",
                value=f"${price_per_unit:,.2f}",
                formula="Total Revenue / Total Units",
                source=f"`{revenue_col}`, `{sales_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Top product by sales
    if product_col and sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        product_sales = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False)
        
        if not product_sales.empty:
            top_product = product_sales.idxmax()
            top_sales = product_sales.max()
            total_sales = product_sales.sum()
            top_share = (top_sales / total_sales * 100) if total_sales > 0 else 0
            
            kpis.append(safe_kpi(
                category="💊 Pharma Sales",
                name="Top Selling Product",
                value=f"{top_product} ({top_sales:,.0f} units)",
                formula="Product with max sales volume",
                source=f"`{product_col}`, `{sales_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💊 Pharma Sales",
                name="Top Product Market Share",
                value=f"{top_share:.2f}%",
                formula="(Top Product / Total) * 100",
                source=f"`{product_col}`, `{sales_col}`",
                confidence=conf,
                warnings="High product concentration" if top_share > 30 else warns
            ))
    
    # Top region
    if region_col and sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        region_sales = df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
        
        if not region_sales.empty:
            top_region = region_sales.idxmax()
            top_region_sales = region_sales.max()
            
            kpis.append(safe_kpi(
                category="💊 Pharma Sales",
                name="Top Market by Sales",
                value=f"{top_region} ({top_region_sales:,.0f} units)",
                formula="Region with max sales",
                source=f"`{region_col}`, `{sales_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Drug class mix
    if class_col and sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
        class_sales = df.groupby(class_col)[sales_col].sum().sort_values(ascending=False)
        
        if not class_sales.empty:
            top_class = class_sales.idxmax()
            top_class_sales = class_sales.max()
            
            kpis.append(safe_kpi(
                category="💊 Pharma Sales",
                name="Top Performing Drug Class",
                value=f"{top_class} ({top_class_sales:,.0f} units)",
                formula="Class with max sales",
                source=f"`{class_col}`, `{sales_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
