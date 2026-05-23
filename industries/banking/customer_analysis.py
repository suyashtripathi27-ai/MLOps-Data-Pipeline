"""
Customer-level KPIs: CLV, engagement, product ownership.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from .reliability import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_customer_metrics(df):
    """Calculates customer behavior and CLV KPIs."""
    kpis = []
    customer_col = _first_column(df, ["customer_id", "customer_code", "cust_id"])
    account_col = _first_column(df, ["account_id", "account_number"])
    amount_col = _first_column(df, ["amount", "balance", "transaction_amount"])
    date_col = _first_column(df, ["transaction_date", "date"])

    if not customer_col or not amount_col:
        return kpis

    conf, warns = evaluate_kpi_confidence(df, [customer_col, amount_col])
    total_customers = df[customer_col].nunique()
    customer_balances = df.groupby(customer_col)[amount_col].sum()
    avg_customer_value = customer_balances.mean()
    max_customer_value = customer_balances.max()

    kpis.append({
        "category": "👥 Customer Analysis",
        "name": "Total Customers",
        "value": f"{total_customers}",
        "formula": "Count(Distinct Customers)",
        "source": f"`{customer_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "👥 Customer Analysis",
        "name": "Avg Customer Balance",
        "value": f"${avg_customer_value:,.2f}",
        "formula": "Mean(Customer Total Balance)",
        "source": f"`{customer_col}`, `{amount_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "👥 Customer Analysis",
        "name": "Max Customer Balance",
        "value": f"${max_customer_value:,.2f}",
        "formula": "Max(Customer Total Balance)",
        "source": f"`{customer_col}`, `{amount_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if account_col:
        accounts_per_customer = df.groupby(customer_col)[account_col].nunique()
        avg_accounts = accounts_per_customer.mean()
        kpis.append({
            "category": "👥 Customer Analysis",
            "name": "Avg Accounts per Customer",
            "value": f"{avg_accounts:.2f}",
            "formula": "Mean(Accounts per Customer)",
            "source": f"`{customer_col}`, `{account_col}`",
            "confidence": conf,
            "warnings": warns,
        })

    if date_col:
        df_date = df.copy()
        df_date["date"] = pd.to_datetime(df[date_col], errors="coerce")
        df_date = df_date.dropna(subset=["date"])
        if not df_date.empty:
            customer_dates = df_date.groupby(customer_col)["date"].agg(["min", "max"])
            customer_dates["lifetime_days"] = (customer_dates["max"] - customer_dates["min"]).dt.days
            avg_lifetime = customer_dates["lifetime_days"].mean()
            kpis.append({
                "category": "👥 Customer Analysis",
                "name": "Avg Customer Lifetime",
                "value": f"{avg_lifetime:.0f} days",
                "formula": "Mean(Max Date - Min Date)",
                "source": f"`{customer_col}`, `{date_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    return kpis
