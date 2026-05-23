"""
Account-level deposit and balance trend KPIs.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_account_metrics(df):
    """Calculates account performance and balance health KPIs."""
    kpis = []
    account_col = _first_column(df, ["account_id", "account_number", "acct_id"])
    amount_col = _first_column(df, ["amount", "transaction_amount", "value"])
    balance_col = _first_column(df, ["balance", "account_balance", "ending_balance"])
    date_col = _first_column(df, ["transaction_date", "date", "posting_date"])

    if not account_col or not amount_col:
        return kpis

    amount_valid, reason = SemanticValidator.is_valid_duration(df[amount_col].fillna(0))
    if not amount_valid:
        return [{
            "category": "💳 Account Analysis",
            "name": "Account Metrics",
            "value": "EXCLUDED",
            "formula": "N/A",
            "source": f"`{amount_col}`",
            "confidence": "Low",
            "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [account_col, amount_col])
    account_activity = df[account_col].nunique()
    total_volume = df[amount_col].sum()
    avg_transaction = df[amount_col].mean()

    kpis.append({
        "category": "💳 Account Analysis",
        "name": "Total Active Accounts",
        "value": f"{account_activity}",
        "formula": "Count(Distinct Account IDs)",
        "source": f"`{account_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "💳 Account Analysis",
        "name": "Total Transaction Volume",
        "value": f"${total_volume:,.2f}",
        "formula": "Sum(Amount)",
        "source": f"`{amount_col}`",
        "confidence": conf,
        "warnings": warns,
    })
    kpis.append({
        "category": "💳 Account Analysis",
        "name": "Avg Transaction Size",
        "value": f"${avg_transaction:,.2f}",
        "formula": "Mean(Amount)",
        "source": f"`{amount_col}`",
        "confidence": conf,
        "warnings": warns,
    })

    if balance_col:
        balance_valid, _ = SemanticValidator.is_valid_duration(df[balance_col].fillna(0))
        if balance_valid:
            avg_balance = df[balance_col].mean()
            min_balance = df[balance_col].min()
            kpis.append({
                "category": "💳 Account Analysis",
                "name": "Avg Account Balance",
                "value": f"${avg_balance:,.2f}",
                "formula": "Mean(Balance)",
                "source": f"`{balance_col}`",
                "confidence": conf,
                "warnings": warns,
            })
            kpis.append({
                "category": "💳 Account Analysis",
                "name": "Min Account Balance",
                "value": f"${min_balance:,.2f}",
                "formula": "Min(Balance)",
                "source": f"`{balance_col}`",
                "confidence": conf,
                "warnings": warns,
            })

    if date_col:
        date_series = pd.to_datetime(df[date_col], errors="coerce")
        date_valid, _ = SemanticValidator.is_valid_datetime(date_series.dropna())
        if date_valid:
            monthly_volume = df.groupby(pd.Grouper(key=date_col, freq='M'))[amount_col].sum()
            if len(monthly_volume) >= 2:
                growth = ((monthly_volume.iloc[-1] - monthly_volume.iloc[0]) / monthly_volume.iloc[0] * 100) if monthly_volume.iloc[0] != 0 else 0
                kpis.append({
                    "category": "💳 Account Analysis",
                    "name": "Account Growth %",
                    "value": f"{growth:.2f}%",
                    "formula": "((Last Month - First Month) / First Month) * 100",
                    "source": f"`{amount_col}`, `{date_col}`",
                    "confidence": conf,
                    "warnings": warns,
                })

    return kpis
