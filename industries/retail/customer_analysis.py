"""
Customer lifetime value, repeat purchases, basket size, and retention metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_customer_metrics(df):
    """Calculates customer behavior and value KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Customer and order metrics are COUNT, not time
    customer_col = first_column(df, ["customer_id", "customer", "user_id", "account_id"])
    order_col = first_column(df, ["order_id", "transaction_id", "invoice_id"])
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "total_sales"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "purchase_date"])
    
    if not customer_col or not revenue_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [customer_col, revenue_col, date_col] if col])
    
    # Total customers
    total_customers = df[customer_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Customers",
        name="Total Unique Customers",
        value=f"{total_customers:,}",
        formula="Count(Distinct Customers)",
        source=f"`{customer_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Basket size
    if order_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        basket_df = df.dropna(subset=[order_col, revenue_col])
        
        if not basket_df.empty:
            basket_size = basket_df.groupby(order_col)[revenue_col].sum().mean()
            
            kpis.append(safe_kpi(
                category="🛍️ Customer Analysis",
                name="Avg Basket Size",
                value=f"${basket_size:,.2f}",
                formula="Mean(Order Revenue)",
                source=f"`{order_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Customer metrics
    if pd.api.types.is_numeric_dtype(df[revenue_col]):
        customer_orders = df.dropna(subset=[customer_col]).groupby(customer_col).size()
        
        if not customer_orders.empty:
            repeat_rate = (customer_orders > 1).sum() / total_customers * 100 if total_customers > 0 else 0
            
            kpis.append(safe_kpi(
                category="👥 Customers",
                name="Repeat Purchase Rate",
                value=f"{repeat_rate:.2f}%",
                formula="(Customers with >1 order / Total) * 100",
                source=f"`{customer_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            # Customer Lifetime Value (CLV)
            customer_revenue = df.dropna(subset=[customer_col]).groupby(customer_col)[revenue_col].sum()
            avg_clv = customer_revenue.mean()
            
            kpis.append(safe_kpi(
                category="👥 Customers",
                name="Avg Customer Lifetime Value",
                value=f"${avg_clv:,.2f}",
                formula="Mean(Total Revenue per Customer)",
                source=f"`{customer_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="👥 Customers",
                name="Avg Orders per Customer",
                value=f"{customer_orders.mean():.2f}",
                formula="Mean(Order Count per Customer)",
                source=f"`{customer_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            # High-value customers
            clv_85 = customer_revenue.quantile(0.85)
            high_value_customers = (customer_revenue >= clv_85).sum()
            high_value_pct = (high_value_customers / len(customer_revenue) * 100) if len(customer_revenue) > 0 else 0
            
            kpis.append(safe_kpi(
                category="👥 Customers",
                name="High-Value Customers (Top 15%)",
                value=f"{high_value_customers:,} ({high_value_pct:.2f}%)",
                formula="Count(CLV >= 85th Percentile)",
                source=f"`{customer_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Retention (⏱️ EXACT DATES - not duration, but points in time)
    if date_col and customer_col:
        retention_df = df[[customer_col]].copy()
        retention_df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        retention_df = retention_df.dropna(subset=["date", customer_col])
        
        if not retention_df.empty:
            dt_valid, _ = SemanticValidator.is_valid_datetime(retention_df["date"].dropna())
            
            if dt_valid:
                retention_df["month"] = retention_df["date"].dt.to_period("M")
                first_month_per_cust = retention_df.groupby(customer_col)["month"].min()
                latest_month = retention_df["month"].max()
                
                if pd.notna(latest_month):
                    retained = (first_month_per_cust < latest_month).sum()
                    cohort_size = len(first_month_per_cust)
                    retention_rate = (retained / cohort_size * 100) if cohort_size > 0 else 0
                    
                    kpis.append(safe_kpi(
                        category="👥 Customers",
                        name="Retention Rate",
                        value=f"{retention_rate:.2f}%",
                        formula="(Active Customers from Earlier Months / Cohort) * 100",
                        source=f"`{customer_col}`, `{date_col}`",
                        confidence=conf,
                        warnings=warns
                    ))
    
    return kpis
