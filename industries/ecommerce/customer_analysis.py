"""
Customer segmentation, LTV, and retention metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_customer_metrics(df):
    """Calculates customer value and retention KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    customer_col = first_column(df, ["customer_id", "customer", "user_id", "account_id", "user_key"])
    order_col = first_column(df, ["order_id", "transaction_id", "invoice_id", "purchase_id"])
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "total_sales", "gmv"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "timestamp", "purchase_date"])
    
    if not customer_col or not revenue_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [customer_col, revenue_col, date_col] if col])
    
    # Basket size
    if order_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        basket_df = df.dropna(subset=[order_col, revenue_col])
        
        if not basket_df.empty:
            basket_value = basket_df.groupby(order_col)[revenue_col].sum().mean()
            
            kpis.append(safe_kpi(
                category="👥 Customer Analysis",
                name="Avg Basket Size",
                value=f"${basket_value:,.2f}",
                formula="Mean(Order Total)",
                source=f"`{order_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Customer metrics
    customer_data = df.dropna(subset=[customer_col])
    
    if not customer_data.empty and pd.api.types.is_numeric_dtype(df[revenue_col]):
        total_customers = customer_data[customer_col].nunique()
        
        kpis.append(safe_kpi(
            category="👥 Customer Analysis",
            name="Total Unique Customers",
            value=f"{total_customers:,}",
            formula="Count(Distinct Customers)",
            source=f"`{customer_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Customer orders
        customer_orders = customer_data.groupby(customer_col).size()
        repeat_rate = (customer_orders > 1).sum() / total_customers * 100 if total_customers > 0 else 0
        
        kpis.append(safe_kpi(
            category="👥 Customer Analysis",
            name="Repeat Purchase Rate",
            value=f"{repeat_rate:.2f}%",
            formula="(Customers with >1 order / Total) * 100",
            source=f"`{customer_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # LTV
        customer_revenue = df.groupby(customer_col)[revenue_col].sum()
        avg_clv = customer_revenue.mean()
        
        kpis.append(safe_kpi(
            category="👥 Customer Analysis",
            name="Avg Customer Lifetime Value",
            value=f"${avg_clv:,.2f}",
            formula="Mean(Total Revenue per Customer)",
            source=f"`{customer_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="👥 Customer Analysis",
            name="Avg Orders per Customer",
            value=f"{customer_orders.mean():.2f}",
            formula="Mean(Orders per Customer)",
            source=f"`{customer_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # High-value customers
        clv_85_threshold = customer_revenue.quantile(0.85)
        high_value_customers = len(customer_revenue[customer_revenue >= clv_85_threshold])
        high_value_pct = (high_value_customers / total_customers * 100) if total_customers > 0 else 0
        
        kpis.append(safe_kpi(
            category="👥 Customer Analysis",
            name="High-Value Customers (Top 15%)",
            value=f"{high_value_customers:,} ({high_value_pct:.2f}%)",
            formula="Count(CLV >= 85th Percentile)",
            source=f"`{customer_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Retention rate (if date column exists)
    if date_col and customer_col:
        retention_df = df[[customer_col]].copy()
        retention_df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        retention_df = retention_df.dropna(subset=["date", customer_col])
        
        if not retention_df.empty:
            retention_df["month"] = retention_df["date"].dt.to_period("M")
            first_month_per_customer = retention_df.groupby(customer_col)["month"].min()
            current_month = retention_df["month"].max()
            
            if pd.notna(current_month):
                retained = (first_month_per_customer < current_month).sum()
                total = len(first_month_per_customer)
                retention_rate = (retained / total * 100) if total > 0 else 0
                
                kpis.append(safe_kpi(
                    category="👥 Customer Analysis",
                    name="Retention Rate",
                    value=f"{retention_rate:.2f}%",
                    formula="(Retained Customers / First Month Cohort) * 100",
                    source=f"`{customer_col}`, `{date_col}`",
                    confidence=conf,
                    warnings=warns
                ))
    
    return kpis
