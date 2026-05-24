"""
Fraud detection and risk metrics for e-commerce.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_fraud_metrics(df):
    """Calculates fraud and security risk KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    fraud_col = first_column(df, ["fraud_flag", "is_fraud", "chargeback_flag", "suspicious_flag", "fraud_score"])
    amount_col = first_column(df, ["order_value", "revenue", "sales", "amount", "transaction_amount"])
    payment_col = first_column(df, ["payment_attempts", "attempts", "retry_count", "failed_attempts"])
    
    if not fraud_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [fraud_col, amount_col, payment_col] if col])
    
    # Fraud rate
    fraud_mask = df[fraud_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'fraud'])
    fraud_count = fraud_mask.sum()
    fraud_rate = (fraud_count / len(df) * 100) if len(df) > 0 else 0
    
    kpis.append(safe_kpi(
        category="🛡️ Fraud Analysis",
        name="Fraud Flag Rate",
        value=f"{fraud_rate:.2f}%",
        formula="(Fraudulent Transactions / Total) * 100",
        source=f"`{fraud_col}`",
        confidence=conf,
        warnings="High fraud rate - Review" if fraud_rate > 5 else warns
    ))
    
    # Fraud revenue share
    if amount_col and pd.api.types.is_numeric_dtype(df[amount_col]):
        fraudulent_amount = df.loc[fraud_mask, amount_col].fillna(0).sum()
        total_amount = df[amount_col].fillna(0).sum()
        fraud_revenue_share = (fraudulent_amount / total_amount * 100) if total_amount > 0 else 0
        
        kpis.append(safe_kpi(
            category="🛡️ Fraud Analysis",
            name="Fraud Revenue Share",
            value=f"{fraud_revenue_share:.2f}%",
            formula="(Fraudulent $ / Total $) * 100",
            source=f"`{fraud_col}`, `{amount_col}`",
            confidence=conf,
            warnings="Significant fraud $ impact" if fraud_revenue_share > 2 else warns
        ))
        
        # High-value fraud
        high_value_threshold = df[amount_col].quantile(0.9)
        high_value_fraud = fraud_mask & (df[amount_col] >= high_value_threshold)
        high_value_fraud_pct = (high_value_fraud.sum() / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="🛡️ Fraud Analysis",
            name="High-Value Fraud (Top 10%)",
            value=f"{high_value_fraud_pct:.2f}%",
            formula="(Fraud in Top 10% by $ / Total) * 100",
            source=f"`{fraud_col}`, `{amount_col}`",
            confidence=conf,
            warnings="Critical: Fraud in high-value transactions" if high_value_fraud_pct > 3 else warns
        ))
    
    # Payment attempts
    if payment_col and pd.api.types.is_numeric_dtype(df[payment_col]):
        valid_attempts = df[payment_col].dropna()
        
        if not valid_attempts.empty:
            avg_attempts = valid_attempts.mean()
            fraud_attempts = df.loc[fraud_mask, payment_col].dropna()
            
            if not fraud_attempts.empty:
                avg_fraud_attempts = fraud_attempts.mean()
                
                kpis.append(safe_kpi(
                    category="🛡️ Fraud Analysis",
                    name="Avg Payment Attempts (Fraudulent)",
                    value=f"{avg_fraud_attempts:.2f}",
                    formula="Mean(Attempts in Fraud Cases)",
                    source=f"`{payment_col}`",
                    confidence=conf,
                    warnings="Multiple retry attempts indicator" if avg_fraud_attempts > 3 else warns
                ))
    
    return kpis
