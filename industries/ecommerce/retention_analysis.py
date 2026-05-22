import pandas as pd

from .common import confidence_for, first_column, safe_kpi


def calc_retention_metrics(df):
    kpis = []
    customer_col = first_column(df, ["customer_id", "customer", "user_id", "account_id"])
    date_col = first_column(df, ["date", "order_date", "transaction_date", "timestamp"])
    order_col = first_column(df, ["order_id", "transaction_id", "invoice_id"])
    if not customer_col or not date_col:
        return kpis

    conf, warns = confidence_for(df, [customer_col, date_col, order_col])
    retention_df = df[[customer_col]].copy()
    retention_df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    retention_df = retention_df.dropna(subset=["date", customer_col])
    if retention_df.empty:
        return kpis

    retention_df["month"] = retention_df["date"].dt.to_period("M")
    active_customers = retention_df.groupby("month")[customer_col].nunique()
    first_month = retention_df.groupby(customer_col)["month"].min()
    current_month = retention_df["month"].max()
    retained = first_month[first_month < current_month].count()
    base = first_month.count()
    retention_rate = (retained / base * 100) if base > 0 else 0
    churn_rate = 100 - retention_rate if base > 0 else 0
    kpis.append(safe_kpi("♻️ Retention Analysis", "Retention Rate", f"{retention_rate:.2f}%", "Customers active before latest month / Total customers * 100", f"`{customer_col}`, `{date_col}`", conf, warns))
    kpis.append(safe_kpi("♻️ Retention Analysis", "Churn Proxy", f"{churn_rate:.2f}%", "100 - Retention Rate", f"`{customer_col}`, `{date_col}`", conf, warns))
    kpis.append(safe_kpi("♻️ Retention Analysis", "Active Customers", f"{active_customers.sum():,.0f}", "Sum(Unique Customers per Month)", f"`{customer_col}`, `{date_col}`", conf, warns))

    if order_col:
        repeat_rate = (df.dropna(subset=[customer_col]).groupby(customer_col)[order_col].nunique() > 1).mean() * 100
        kpis.append(safe_kpi("♻️ Retention Analysis", "Repeat Purchase Rate", f"{repeat_rate:.2f}%", "Customers with >1 order / Total customers * 100", f"`{customer_col}`, `{order_col}`", conf, warns))

    return kpis
