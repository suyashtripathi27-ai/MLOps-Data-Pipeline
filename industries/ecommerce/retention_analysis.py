"""
Customer retention, churn, and repeat purchase metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_retention_metrics(df):
    """Calculates customer retention KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    customer_col = first_column(df, ["customer_id", "customer", "user_id", "account_id"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "purchase_date", "created_at"])
    revenue_col = first_column(df, ["revenue", "order_value", "sales", "amount"])
    status_col = first_column(df, ["customer_status", "status", "lifecycle_stage", "churn_flag"])
    
    if not customer_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [customer_col, date_col, revenue_col, status_col] if col])
    
    # Basic customer count
    total_customers = df[customer_col].nunique()
    
    kpis.append(safe_kpi(
        category="👥 Retention",
        name="Total Customers",
        value=f"{total_customers:,}",
        formula="Count(Distinct Customers)",
        source=f"`{customer_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Repeat customers
    customer_purchase_count = df[customer_col].value_counts()
    repeat_customers = (customer_purchase_count > 1).sum()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    kpis.append(safe_kpi(
        category="👥 Retention",
        name="Repeat Customers",
        value=f"{repeat_customers:,} ({repeat_rate:.2f}%)",
        formula="Customers with >1 Purchase / Total",
        source=f"`{customer_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # One-time customers
    one_time_customers = (customer_purchase_count == 1).sum()
    one_time_rate = (one_time_customers / total_customers * 100) if total_customers > 0 else 0
    
    kpis.append(safe_kpi(
        category="👥 Retention",
        name="One-Time Customers",
        value=f"{one_time_customers:,} ({one_time_rate:.2f}%)",
        formula="Customers with Exactly 1 Purchase / Total",
        source=f"`{customer_col}`",
        confidence=conf,
        warnings="High churn risk" if one_time_rate > 80 else warns
    ))
    
    # Cohort retention (if date exists)
    if date_col:
        retention_df = df[[customer_col]].copy()
        retention_df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        retention_df = retention_df.dropna(subset=["date", customer_col])
        
        if not retention_df.empty:
            retention_df["month"] = retention_df["date"].dt.to_period("M")
            first_month_per_cust = retention_df.groupby(customer_col)["month"].min()
            latest_month = retention_df["month"].max()
            
            if pd.notna(latest_month):
                retained_count = (first_month_per_cust < latest_month).sum()
                cohort_size = len(first_month_per_cust)
                cohort_retention = (retained_count / cohort_size * 100) if cohort_size > 0 else 0
                
                kpis.append(safe_kpi(
                    category="👥 Retention",
                    name="Cohort Retention Rate",
                    value=f"{cohort_retention:.2f}%",
                    formula="Active from First Month / Cohort Size * 100",
                    source=f"`{customer_col}`, `{date_col}`",
                    confidence=conf,
                    warnings=warns
                ))
    
    # Churn analysis
    if status_col:
        status_lower = df[status_col].astype(str).str.lower()
        churned = status_lower.isin(['churned', 'churn', 'inactive', 'lost']).sum()
        churn_rate = (churned / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="👥 Retention",
            name="Churn Rate",
            value=f"{churn_rate:.2f}%",
            formula="Churned Customers / Total * 100",
            source=f"`{status_col}`",
            confidence=conf,
            warnings="High churn" if churn_rate > 30 else warns
        ))
    
    # Revenue per retention cohort
    if revenue_col and date_col and pd.api.types.is_numeric_dtype(df[revenue_col]):
        cohort_revenue = df.groupby(customer_col)[revenue_col].sum()
        avg_revenue_retained = cohort_revenue[cohort_revenue > 0].mean()
        
        kpis.append(safe_kpi(
            category="👥 Retention",
            name="Avg Retained Customer Revenue",
            value=f"${avg_revenue_retained:,.2f}",
            formula="Mean(Revenue) for Repeat Customers",
            source=f"`{customer_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
