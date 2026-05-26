"""
Customer segmentation, LTV, and retention metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
# Moderate thresholds - focus on growth velocity vs strict compliance
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,        # ✅ Moderate - tech platforms have data quality
    "score_deduction_for_warning": 12,  # ✅ Lower penalty - more lenient than banking
    "low_confidence_threshold": 35,     # ✅ Higher threshold = harder to flag "Low"
}

def calc_customer_metrics(df, enable_debug=False):
    """
    Calculate customer value KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    # ✅ OPTION 2: Initialize with ecommerce industry config
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    
    # ✅ OPTION 1: Enable tracing for enterprise observability
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    cust_col, cust_series = engine.get_column(["customer_id", "customer", "user_id", "account_id", "user_key"])
    order_col, order_series = engine.get_column(["order_id", "transaction_id", "invoice_id", "purchase_id"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "order_value", "total_sales", "gmv"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "order_date", "timestamp", "purchase_date"])
    
    if cust_col is not None and revenue_col is not None:
        total_customers = cust_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="👥 Customer Analysis", name="Total Unique Customers",
            value=f"{total_customers:,}", formula="Count(Distinct Customers)", source=f"`{cust_col}`"
        ))
        
        # Customer orders
        customer_orders = df.groupby(cust_col).size()
        repeat_rate = (customer_orders > 1).sum() / total_customers * 100 if total_customers > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="👥 Customer Analysis", name="Repeat Purchase Rate",
            value=f"{repeat_rate:.2f}%", formula="(Customers with >1 order / Total) * 100", source=f"`{cust_col}`"
        ))
        
        # LTV
        customer_revenue = df.groupby(cust_col)[revenue_col].sum()
        avg_clv = customer_revenue.mean()
        
        kpis.append(engine.build_kpi(
            category="👥 Customer Analysis", name="Avg Customer Lifetime Value",
            value=f"${avg_clv:,.2f}", formula="Mean(Total Revenue per Customer)", source=f"`{cust_col}`, `{revenue_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="👥 Customer Analysis", name="Avg Orders per Customer",
            value=f"{customer_orders.mean():.2f}", formula="Mean(Orders per Customer)", source=f"`{cust_col}`"
        ))
        
        # High-value customers
        clv_85_threshold = customer_revenue.quantile(0.85)
        high_value_customers = len(customer_revenue[customer_revenue >= clv_85_threshold])
        high_value_pct = (high_value_customers / total_customers * 100) if total_customers > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="👥 Customer Analysis", name="High-Value Customers (Top 15%)",
            value=f"{high_value_customers:,} ({high_value_pct:.2f}%)", formula="Count(CLV >= 85th Percentile)", source=f"`{cust_col}`, `{revenue_col}`"
        ))
    else:
        kpis.append(engine.log_missing("👥 Customer Analysis", "Customer Metrics", "Missing 'customer_id' or numeric 'revenue'."))
    
    # Retention rate (if date column exists)
    if date_col is not None and cust_col is not None:
        df_temp = pd.concat([cust_series, date_series], axis=1).dropna()
        if len(df_temp) > 0:
            df_temp["month"] = df_temp[date_col].dt.to_period("M")
            first_month_per_customer = df_temp.groupby(cust_col)["month"].min()
            current_month = df_temp["month"].max()
            
            if pd.notna(current_month):
                retained = (first_month_per_customer < current_month).sum()
                total = len(first_month_per_customer)
                retention_rate = (retained / total * 100) if total > 0 else 0
                
                kpis.append(engine.build_kpi(
                    category="👥 Customer Analysis", name="Retention Rate",
                    value=f"{retention_rate:.2f}%", formula="(Retained Customers / First Month Cohort) * 100", source=f"`{cust_col}`, `{date_col}`"
                ))
    
    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
