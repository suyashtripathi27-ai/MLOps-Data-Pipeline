"""
Customer-level KPIs: CLV, engagement, product ownership.
"""
import pandas as pd
from utils.kpi_helpers import (
    first_column, safe_kpi, excluded_kpi, confidence_for, safe_exists, safe_numeric, safe_numeric_series, safe_datetime
)

def calc_customer_metrics(df):
    kpis = []
    missing_capabilities = []
    
    if len(df) == 0: return kpis
    
    customer_col = first_column(df, ["customer_id", "customer_code", "cust_id"])
    account_col = first_column(df, ["account_id", "account_number"])
    amount_col = first_column(df, ["amount", "balance", "transaction_amount"])
    date_col = first_column(df, ["transaction_date", "date"])

    conf, warns = confidence_for(df, [customer_col, amount_col, account_col, date_col])
    
    if safe_exists(df, customer_col):
        total_customers = df[customer_col].nunique()
        kpis.append(safe_kpi(
            category="👥 Customer Analysis", name="Total Customers",
            value=f"{total_customers}", formula="Count(Distinct Customers)",
            source=f"`{customer_col}`", confidence=conf, warnings=warns
        ))

        if safe_numeric(df, amount_col):
            clean_amount = safe_numeric_series(df, amount_col)
            customer_balances = clean_amount.groupby(df[customer_col]).sum()
            
            kpis.append(safe_kpi(
                category="👥 Customer Analysis", name="Avg Customer Balance",
                value=f"${customer_balances.mean():,.2f}", formula="Mean(Customer Total Balance)",
                source=f"`{customer_col}`, `{amount_col}`", confidence=conf, warnings=warns
            ))
            kpis.append(safe_kpi(
                category="👥 Customer Analysis", name="Max Customer Balance",
                value=f"${customer_balances.max():,.2f}", formula="Max(Customer Total Balance)",
                source=f"`{customer_col}`, `{amount_col}`", confidence=conf, warnings=warns
            ))
        else:
            missing_capabilities.append("Customer valuation unavailable: Missing numeric 'amount'.")

        if safe_exists(df, account_col):
            avg_accounts = df.groupby(customer_col)[account_col].nunique().mean()
            kpis.append(safe_kpi(
                category="👥 Customer Analysis", name="Avg Accounts per Customer",
                value=f"{avg_accounts:.2f}", formula="Mean(Accounts per Customer)",
                source=f"`{customer_col}`, `{account_col}`", confidence=conf, warnings=warns
            ))
        else:
            missing_capabilities.append("Customer engagement unavailable: Missing 'account_id'.")

        if safe_datetime(df, date_col):
            df_date = df.dropna(subset=[date_col]).copy()
            df_date["date"] = pd.to_datetime(df_date[date_col], errors="coerce")
            
            customer_dates = df_date.groupby(customer_col)["date"].agg(["min", "max"])
            customer_dates["lifetime_days"] = (customer_dates["max"] - customer_dates["min"]).dt.days
            
            kpis.append(safe_kpi(
                category="👥 Customer Analysis", name="Avg Customer Lifetime",
                value=f"{customer_dates['lifetime_days'].mean():.0f} days", formula="Mean(Max Date - Min Date)",
                source=f"`{customer_col}`, `{date_col}`", confidence=conf, warnings=warns
            ))
        else:
            missing_capabilities.append("Lifetime analysis unavailable: Missing valid 'date'.")

    else:
        missing_capabilities.append("Customer Analytics unavailable: Missing 'customer_id' column.")

    for missing in missing_capabilities:
        kpis.append(excluded_kpi(category="⚠️ System Audit", name="Data Gap Detected", source="Diagnostic", reason=missing))

    return kpis
