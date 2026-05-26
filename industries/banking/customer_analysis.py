"""
Customer-level KPIs: CLV, engagement, product ownership.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

BANKING_CONFIG = {
    "missing_data_threshold": 5,        
    "score_deduction_for_warning": 20,  
    "low_confidence_threshold": 25,     
}

def calc_customer_metrics(df, enable_debug=False):
    """
    Calculate customer-level KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
   
    engine = KPIEngine(df, industry_config=BANKING_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0: 
        return kpis
    
    cust_col, cust_series = engine.get_column(["customer_id", "customer_code", "cust_id"])
    acct_col, acct_series = engine.get_column(["account_id", "account_number"])
    amt_col, amt_series = engine.get_numeric(["amount", "balance", "transaction_amount"])
    date_col, date_series = engine.get_datetime(["transaction_date", "date"])
    
    if cust_col is not None:
        total_customers = cust_series.nunique()
        kpis.append(engine.build_kpi(
            category="👥 Customer Analysis", name="Total Customers",
            value=f"{total_customers}", formula="Count(Distinct Customers)", source=f"`{cust_col}`"
        ))

        if amt_col is not None:
            df_temp = pd.concat([cust_series, amt_series], axis=1).dropna()
            customer_balances = df_temp.groupby(cust_col)[amt_col].sum()
            
            kpis.append(engine.build_kpi(
                category="👥 Customer Analysis", name="Avg Customer Balance",
                value=f"${customer_balances.mean():,.2f}", formula="Mean(Customer Total Balance)", source=f"`{cust_col}`, `{amt_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="👥 Customer Analysis", name="Max Customer Balance",
                value=f"${customer_balances.max():,.2f}", formula="Max(Customer Total Balance)", source=f"`{cust_col}`, `{amt_col}`"
            ))
        else:
            kpis.append(engine.log_missing("👥 Customer Analysis", "Customer Balances", "Missing numeric 'amount'."))

        if acct_col is not None:
            df_temp = pd.concat([cust_series, acct_series], axis=1).dropna()
            avg_accounts = df_temp.groupby(cust_col)[acct_col].nunique().mean()
            kpis.append(engine.build_kpi(
                category="👥 Customer Analysis", name="Avg Accounts per Customer",
                value=f"{avg_accounts:.2f}", formula="Mean(Accounts per Customer)", source=f"`{cust_col}`, `{acct_col}`"
            ))
        else:
            kpis.append(engine.log_missing("👥 Customer Analysis", "Customer Engagement", "Missing 'account_id'."))

        if date_col is not None:
            df_temp = pd.concat([cust_series, date_series], axis=1).dropna()
            customer_dates = df_temp.groupby(cust_col)[date_col].agg(["min", "max"])
            customer_dates["lifetime_days"] = (customer_dates["max"] - customer_dates["min"]).dt.days
            
            kpis.append(engine.build_kpi(
                category="👥 Customer Analysis", name="Avg Customer Lifetime",
                value=f"{customer_dates['lifetime_days'].mean():.0f} days", formula="Mean(Max - Min Date)", source=f"`{cust_col}`, `{date_col}`"
            ))
        else:
            kpis.append(engine.log_missing("👥 Customer Analysis", "Customer Lifetime", "Missing valid 'date'."))
    else:
        kpis.append(engine.log_missing("👥 Customer Analysis", "Customer Metrics", "Missing 'customer_id' column."))

   
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
