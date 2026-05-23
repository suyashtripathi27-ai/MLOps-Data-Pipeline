import pandas as pd
from .common import confidence_for, first_column, safe_kpi
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def calc_customer_metrics(df):
    kpis = []
    customer_col = first_column(df, ["customer_id", "customer", "user_id", "account_id"])
    order_col = first_column(df, ["order_id", "transaction_id", "invoice_id"])
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "total_sales"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "timestamp"])
    if not customer_col or not revenue_col:
        return kpis

    conf, warns = confidence_for(df, [customer_col, revenue_col] + ([date_col] if date_col else []))

    if order_col:
        basket_df = df.dropna(subset=[order_col, revenue_col])
        if not basket_df.empty:
            basket_value = basket_df.groupby(order_col)[revenue_col].sum().mean()
            kpis.append(safe_kpi("🧑‍💻 Customer Analysis", "Avg Basket Size", f"${basket_value:,.2f}", "Mean(Order Revenue)", f"`{order_col}`, `{revenue_col}`", conf, warns))

    customer_orders = df.dropna(subset=[customer_col]).groupby(customer_col).size()
    if not customer_orders.empty:
        repeat_rate = (customer_orders > 1).mean() * 100
        avg_revenue_per_customer = df.groupby(customer_col)[revenue_col].sum().mean()
        clv = avg_revenue_per_customer * customer_orders.mean()
        kpis.append(safe_kpi("🧑‍💻 Customer Analysis", "Repeat Purchase Rate", f"{repeat_rate:.2f}%", "Customers with >1 order / Total customers * 100", f"`{customer_col}`", conf, warns))
        kpis.append(safe_kpi("🧑‍💻 Customer Analysis", "Customer Lifetime Value", f"${clv:,.2f}", "Avg Revenue per Customer * Avg Purchase Frequency", f"`{customer_col}`, `{revenue_col}`", conf, warns))
        kpis.append(safe_kpi("🧑‍💻 Customer Analysis", "Avg Orders per Customer", f"{customer_orders.mean():.2f}", "Total Orders / Unique Customers", f"`{customer_col}`", conf, warns))

    if date_col:
        retention_df = df[[customer_col]].copy()
        retention_df["date"] = pd.to_datetime(df[date_col], errors="coerce")
        retention_df = retention_df.dropna(subset=["date", customer_col])
        if not retention_df.empty:
            retention_df["month"] = retention_df["date"].dt.to_period("M")
            first_month = retention_df.groupby(customer_col)["month"].min()
            current_month = retention_df["month"].max()
            retained = first_month[first_month < current_month].count()
            base = first_month.count()
            retention_rate = (retained / base * 100) if base > 0 else 0
            kpis.append(safe_kpi("🧑‍💻 Customer Analysis", "Retention Rate", f"{retention_rate:.2f}%", "Customers active before latest month / Total customers * 100", f"`{customer_col}`, `{date_col}`", conf, warns))

    return kpis
