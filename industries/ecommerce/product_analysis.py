import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator


def calc_product_metrics(df):
    kpis = []
    product_col = first_column(df, ["product_id", "sku", "item_id", "product_name"])
    category_col = first_column(df, ["category", "product_category", "department"])
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "total_sales"])
    units_col = first_column(df, ["units_sold", "quantity", "items_sold", "units"])
    rating_col = first_column(df, ["rating", "review_rating", "score"])
    if not product_col:
        return kpis

    conf, warns = confidence_for(df, [product_col, category_col, revenue_col, units_col, rating_col])
    unique_products = df[product_col].nunique(dropna=True)
    kpis.append(safe_kpi("🧩 Product Analysis", "Unique Products", f"{unique_products:,}", "Distinct(Product IDs)", f"`{product_col}`", conf, warns))

    if revenue_col:
        by_product = df.dropna(subset=[product_col, revenue_col]).groupby(product_col)[revenue_col].sum()
        if not by_product.empty:
            top_share = by_product.head(10).sum() / by_product.sum() * 100 if by_product.sum() > 0 else 0
            kpis.append(safe_kpi("🧩 Product Analysis", "Top 10 Product Revenue Share", f"{top_share:.2f}%", "Top 10 Products / Total Revenue * 100", f"`{product_col}`, `{revenue_col}`", conf, warns))

    if category_col and revenue_col:
        category_share = df.dropna(subset=[category_col, revenue_col]).groupby(category_col)[revenue_col].sum().sort_values(ascending=False)
        if not category_share.empty:
            kpis.append(safe_kpi("🧩 Product Analysis", "Top Category Revenue", f"${category_share.iloc[0]:,.2f}", "Max(Category Revenue)", f"`{category_col}`, `{revenue_col}`", conf, warns))

    if units_col:
        avg_units = df[units_col].dropna().mean()
        kpis.append(safe_kpi("🧩 Product Analysis", "Avg Units per Product", f"{avg_units:.2f}", "Mean(Units Sold)", f"`{units_col}`", conf, warns))

    if rating_col:
        avg_rating = df[rating_col].dropna().mean()
        kpis.append(safe_kpi("🧩 Product Analysis", "Avg Rating", f"{avg_rating:.2f}", "Mean(Rating)", f"`{rating_col}`", conf, warns))

    return kpis
