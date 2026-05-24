"""
Fraud detection and transaction anomaly metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_fraud_metrics(df):
    """Calculates fraud detection KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    fraud_col = first_column(df, ["fraud_flag", "is_fraud", "fraud_score", "suspicious_flag"])
    amount_col = first_column(df, ["amount", "transaction_amount", "value"])
    transaction_col = first_column(df, ["transaction_id", "txn_id"])
    fraud_type_col = first_column(df, ["fraud_type", "anomaly_type", "suspicious_activity"])
    
    if not fraud_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [fraud_col, amount_col, transaction_col, fraud_type_col] if col])
    
    # Fraud detection rate
    fraud_mask = df[fraud_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'fraud'])
    fraud_count = fraud_mask.sum()
    fraud_rate = (fraud_count / len(df) * 100) if len(df) > 0 else 0
    
    kpis.append(safe_kpi(
        category="🔍 Fraud Detection",
        name="Flagged Transactions",
        value=f"{fraud_count:,} ({fraud_rate:.2f}%)",
        formula="Count(Fraud Flag) / Total * 100",
        source=f"`{fraud_col}`",
        confidence=conf,
        warnings="High fraud flag rate" if fraud_rate > 5 else warns
    ))
    
    # Fraud amount
    if amount_col and pd.api.types.is_numeric_dtype(df[amount_col]):
        fraudulent_amount = df.loc[fraud_mask, amount_col].fillna(0).sum()
        total_amount = df[amount_col].fillna(0).sum()
        fraud_amount_pct = (fraudulent_amount / total_amount * 100) if total_amount > 0 else 0
        
        kpis.append(safe_kpi(
            category="🔍 Fraud Detection",
            name="Total Flagged Amount",
            value=f"${fraudulent_amount:,.2f}",
            formula="Sum(Amount where Fraud=True)",
            source=f"`{fraud_col}`, `{amount_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🔍 Fraud Detection",
            name="Fraud Amount as % of Total",
            value=f"{fraud_amount_pct:.2f}%",
            formula="(Fraud $ / Total $) * 100",
            source=f"`{fraud_col}`, `{amount_col}`",
            confidence=conf,
            warnings="Significant fraud $" if fraud_amount_pct > 1 else warns
        ))
        
        # High-value fraud
        high_value_threshold = df[amount_col].quantile(0.90)
        high_value_fraud = fraud_mask & (df[amount_col] >= high_value_threshold)
        high_value_fraud_pct = (high_value_fraud.sum() / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="🔍 Fraud Detection",
            name="High-Value Fraud (Top 10%)",
            value=f"{high_value_fraud_pct:.2f}%",
            formula="(Fraud in Top 10% by $ / Total) * 100",
            source=f"`{fraud_col}`, `{amount_col}`",
            confidence=conf,
            warnings="Critical: Fraud in large transactions" if high_value_fraud_pct > 2 else warns
        ))
    
    # Fraud type breakdown
    if fraud_type_col:
        fraud_types = df[fraud_mask][fraud_type_col].value_counts()
        
        if not fraud_types.empty:
            top_fraud_type = fraud_types.idxmax()
            
            kpis.append(safe_kpi(
                category="🔍 Fraud Detection",
                name="Most Common Fraud Type",
                value=f"{top_fraud_type} ({fraud_types.max()} cases)",
                formula="Fraud type with most occurrences",
                source=f"`{fraud_type_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
