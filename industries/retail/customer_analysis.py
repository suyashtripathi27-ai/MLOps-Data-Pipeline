import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_customer_metrics(df):
    """Calculates basket, repeat, CLV, and retention KPIs."""
    kpis = []
    customer_col = _first_column(df, ["customer_id", "customer", "user_id"])
    order_col = _first_column(df, ["order_id", "transaction_id", "invoice_id"])
    revenue_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    date_col = _first_column(df, ["date", "transaction_date", "order_date"])
    if not customer_col or not revenue_col:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [customer_col, revenue_col] + ([date_col] if date_col else []))

    if order_col:
        basket_df = df.dropna(subset=[order_col, revenue_col])
        if not basket_df.empty:
            basket_size = basket_df.groupby(order_col)[revenue_col].sum().mean()
            kpis.append({
                "category": "🛍️ Customer Analysis",
                "name": "Avg Basket Size",
                "value": f"${basket_size:,.2f}",
                "formula": "Mean(Order Revenue)",
                "source": f"`{order_col}`, `{revenue_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    customer_orders = df.dropna(subset=[customer_col]).groupby(customer_col).size()
    if not customer_orders.empty:
        repeat_rate = (customer_orders > 1).mean() * 100
        avg_revenue_per_customer = df.groupby(customer_col)[revenue_col].sum().mean()
        clv = avg_revenue_per_customer * customer_orders.mean()
        kpis.append({
            "category": "🛍️ Customer Analysis",
            "name": "Repeat Purchase Rate",
            "value": f"{repeat_rate:.2f}%",
            "formula": "Customers with >1 order / Total customers * 100",
            "source": f"`{customer_col}`",
            "confidence": conf,
            "warnings": warns,
        })
        kpis.append({
            "category": "🛍️ Customer Analysis",
            "name": "CLV",
            "value": f"${clv:,.2f}",
            "formula": "Avg Revenue per Customer * Avg Purchase Frequency",
            "source": f"`{customer_col}`, `{revenue_col}`",
            "confidence": conf,
            "warnings": warns,
        })

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
            kpis.append({
                "category": "🛍️ Customer Analysis",
                "name": "Retention Rate",
                "value": f"{retention_rate:.2f}%",
                "formula": "Customers active before latest month / Total customers * 100",
                "source": f"`{customer_col}`, `{date_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    return kpis
