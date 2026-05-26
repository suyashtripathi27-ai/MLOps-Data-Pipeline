"""
Customer retention, churn, and repeat purchase metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_retention_metrics(df, enable_debug=False):
    """
    Calculate retention KPIs with optional execution tracing.
    
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
    
    customer_col, customer_series = engine.get_column(["customer_id", "customer", "user_id", "account_id"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "order_date", "purchase_date", "created_at"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "order_value", "sales", "amount"])
    status_col, status_series = engine.get_column(["customer_status", "status", "lifecycle_stage", "churn_flag"])
    
    if customer_col is not None:
        total_customers = customer_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="👥 Retention", name="Total Customers",
            value=f"{total_customers:,}", formula="Count(Distinct Customers)", source=f"`{customer_col}`"
        ))
        
        # Repeat customers
        customer_purchase_count = df[customer_col].value_counts()
        repeat_customers = (customer_purchase_count > 1).sum()
        repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="👥 Retention", name="Repeat Customers",
            value=f"{repeat_customers:,} ({repeat_rate:.2f}%)", formula="Customers with >1 Purchase / Total", source=f"`{customer_col}`"
        ))
        
        # One-time customers
        one_time_customers = (customer_purchase_count == 1).sum()
        one_time_rate = (one_time_customers / total_customers * 100) if total_customers > 0 else 0
        warn_msg = "High churn risk" if one_time_rate > 80 else "None"
        
        kpis.append(engine.build_kpi(
            category="👥 Retention", name="One-Time Customers",
            value=f"{one_time_customers:,} ({one_time_rate:.2f}%)", formula="Customers with Exactly 1 Purchase / Total", source=f"`{customer_col}`",
            warnings=warn_msg
        ))
    else:
        kpis.append(engine.log_missing("👥 Retention", "Retention", "Missing 'customer_id'."))
    
    # Cohort retention
    if date_col is not None and customer_col is not None:
        df_temp = pd.concat([customer_series, date_series], axis=1).dropna()
        if len(df_temp) > 0:
            df_temp["month"] = df_temp[date_col].dt.to_period("M")
            first_month_per_cust = df_temp.groupby(customer_col)["month"].min()
            latest_month = df_temp["month"].max()
            
            if pd.notna(latest_month):
                retained_count = (first_month_per_cust < latest_month).sum()
                cohort_size = len(first_month_per_cust)
                cohort_retention = (retained_count / cohort_size * 100) if cohort_size > 0 else 0
                
                kpis.append(engine.build_kpi(
                    category="👥 Retention", name="Cohort Retention Rate",
                    value=f"{cohort_retention:.2f}%", formula="Active from First Month / Cohort Size * 100", source=f"`{customer_col}`, `{date_col}`"
                ))
    
    # Churn analysis
    if status_col is not None:
        status_lower = status_series.astype(str).str.lower()
        churned = status_lower.isin(['churned', 'churn', 'inactive', 'lost']).sum()
        churn_rate = (churned / len(df) * 100) if len(df) > 0 else 0
        warn_msg = "High churn" if churn_rate > 30 else "None"
        
        kpis.append(engine.build_kpi(
            category="👥 Retention", name="Churn Rate",
            value=f"{churn_rate:.2f}%", formula="Churned Customers / Total * 100", source=f"`{status_col}`",
            warnings=warn_msg
        ))
    
    # Revenue per retention cohort
    if revenue_col is not None and customer_col is not None:
        cohort_revenue = df.groupby(customer_col)[revenue_col].sum()
        avg_revenue_retained = cohort_revenue[cohort_revenue > 0].mean()
        
        kpis.append(engine.build_kpi(
            category="👥 Retention", name="Avg Retained Customer Revenue",
            value=f"${avg_revenue_retained:,.2f}", formula="Mean(Revenue) for Repeat Customers", source=f"`{customer_col}`, `{revenue_col}`"
        ))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
