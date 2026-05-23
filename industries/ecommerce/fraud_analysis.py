import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator


def calc_fraud_metrics(df):
    kpis = []
    fraud_col = first_column(df, ["fraud_flag", "is_fraud", "chargeback_flag", "suspicious_flag"])
    amount_col = first_column(df, ["order_value", "revenue", "sales", "amount"])
    payment_col = first_column(df, ["payment_attempts", "attempts", "retry_count"])
    if not fraud_col:
        return kpis

    conf, warns = confidence_for(df, [fraud_col, amount_col, payment_col])
    fraud_series = bool_mask(df[fraud_col])
    fraud_rate = fraud_series.mean() * 100
    kpis.append(safe_kpi("🛡️ Fraud Analysis", "Fraud Flag Rate", f"{fraud_rate:.2f}%", "Fraud Orders / Total Orders * 100", f"`{fraud_col}`", conf, warns))

    if amount_col:
        fraudulent_amount = df.loc[fraud_series, amount_col].fillna(0).sum()
        total_amount = df[amount_col].fillna(0).sum()
        fraud_share = (fraudulent_amount / total_amount * 100) if total_amount > 0 else 0
        kpis.append(safe_kpi("🛡️ Fraud Analysis", "Fraud Revenue Share", f"{fraud_share:.2f}%", "Fraudulent Revenue / Total Revenue * 100", f"`{fraud_col}`, `{amount_col}`", conf, warns))

    if payment_col:
        avg_attempts = df[payment_col].dropna().mean()
        kpis.append(safe_kpi("🛡️ Fraud Analysis", "Avg Payment Attempts", f"{avg_attempts:.2f}", "Mean(Payment Attempts)", f"`{payment_col}`", conf, warns))

    if amount_col:
        valid_amounts = df[amount_col].dropna()
        high_value_threshold = valid_amounts.quantile(0.9) if not valid_amounts.empty else 0
        high_value_mask = fraud_series & (df[amount_col] >= high_value_threshold) if high_value_threshold else fraud_series & False
        risk_share = (high_value_mask.mean() * 100) if len(df) > 0 else 0
        kpis.append(safe_kpi("🛡️ Fraud Analysis", "High-Value Fraud Share", f"{risk_share:.2f}%", "Fraud Rows in Top Decile Order Values / Total Rows * 100", f"`{fraud_col}`, `{amount_col}`", conf, warns))

    return kpis
