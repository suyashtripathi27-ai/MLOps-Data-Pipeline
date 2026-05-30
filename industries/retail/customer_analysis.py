"""
Customer lifetime value, repeat purchases, basket size, and retention metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine
from utils.validator import SemanticValidator

RETAIL_CONFIG = {"missing_data_threshold": 8, "score_deduction_for_warning": 12, "low_confidence_threshold": 35}

def calc_customer_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=RETAIL_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    customer_col, customer_series = engine.get_column(["customer_id", "customer", "user_id", "account_id"])
    order_col, order_series = engine.get_column(["order_id", "transaction_id", "invoice_id"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "order_value", "total_sales"])
    date_col, date_series = engine.get_datetime(["date", "transaction_date", "order_date", "purchase_date"])
    
    if customer_col is not None:
        total_customers = customer_series.nunique()
        kpis.append(engine.build_kpi(
            "👥 Customers", "Total Unique Customers", f"{total_customers:,}", 
            "Count(Distinct Customers)", f"`{customer_col}`"
        ))
        
        if revenue_col is not None:
            calc_df = pd.concat([customer_series, revenue_series], axis=1).dropna()
            if len(calc_df) > 0:
                customer_orders = calc_df.groupby(customer_col).size()
                customer_revenue = calc_df.groupby(customer_col)[revenue_col].sum()
                
                repeat_rate = (customer_orders > 1).sum() / total_customers * 100 if total_customers > 0 else 0
                avg_clv = customer_revenue.mean()
                
                clv_85 = customer_revenue.quantile(0.85)
                high_val_cust = (customer_revenue >= clv_85).sum()
                high_val_pct = (high_val_cust / len(customer_revenue) * 100) if len(customer_revenue) > 0 else 0
                
                kpis.append(engine.build_kpi("👥 Customers", "Repeat Purchase Rate", f"{repeat_rate:.2f}%", "Customers >1 Order / Total * 100", f"`{customer_col}`"))
                kpis.append(engine.build_kpi("👥 Customers", "Avg Customer Lifetime Value", f"${avg_clv:,.2f}", "Mean(Total Revenue per Customer)", f"`{customer_col}`, `{revenue_col}`"))
                kpis.append(engine.build_kpi("👥 Customers", "Avg Orders per Customer", f"{customer_orders.mean():.2f}", "Mean(Order Count per Customer)", f"`{customer_col}`"))
                kpis.append(engine.build_kpi("👥 Customers", "High-Value Customers (Top 15%)", f"{high_val_cust:,} ({high_val_pct:.2f}%)", "Count(CLV >= 85th Percentile)", f"`{customer_col}`, `{revenue_col}`"))
        else:
            kpis.append(engine.log_missing("👥 Customers", "Customer Revenue", "Missing numeric 'revenue'."))
    else:
        kpis.append(engine.log_missing("👥 Customers", "Customers", "Missing 'customer_id' column."))

    if order_col is not None and revenue_col is not None:
        basket_df = pd.concat([order_series, revenue_series], axis=1).dropna()
        if len(basket_df) > 0:
            basket_size = basket_df.groupby(order_col)[revenue_col].sum().mean()
            kpis.append(engine.build_kpi("🛍️ Customer Analysis", "Avg Basket Size", f"${basket_size:,.2f}", "Mean(Order Revenue)", f"`{order_col}`, `{revenue_col}`"))
    else:
        kpis.append(engine.log_missing("🛍️ Customer Analysis", "Basket Size", "Requires 'order_id' and numeric 'revenue'."))

    if date_col is not None and customer_col is not None:
        retention_df = pd.concat([customer_series, date_series], axis=1).dropna()
        if len(retention_df) > 0:
            retention_df["month"] = retention_df[date_col].dt.to_period("M")
            first_month = retention_df.groupby(customer_col)["month"].min()
            latest_month = retention_df["month"].max()
            
            if pd.notna(latest_month):
                retained = (first_month < latest_month).sum()
                cohort_size = len(first_month)
                retention_rate = (retained / cohort_size * 100) if cohort_size > 0 else 0
                kpis.append(engine.build_kpi("👥 Customers", "Retention Rate", f"{retention_rate:.2f}%", "Active Customers from Earlier Months / Cohort * 100", f"`{customer_col}`, `{date_col}`"))

    if enable_debug: engine.print_execution_log()
    return kpis
