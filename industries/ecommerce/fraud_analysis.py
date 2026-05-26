"""
Fraud detection and risk metrics for e-commerce.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,        
    "score_deduction_for_warning": 12,  
    "low_confidence_threshold": 35,     
} 

def calc_fraud_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    fraud_col, fraud_series = engine.get_column(["fraud_flag", "is_fraud", "chargeback_flag", "suspicious_flag", "fraud_score"])
    amount_col, amount_series = engine.get_numeric(["order_value", "revenue", "sales", "amount", "transaction_amount"])
    payment_col, payment_series = engine.get_numeric(["payment_attempts", "attempts", "retry_count", "failed_attempts"])
    
    if fraud_col is not None:
        fraud_mask = fraud_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'fraud'])
        fraud_count = fraud_mask.sum()
        fraud_rate = (fraud_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🛡️ Fraud Analysis", name="Fraud Flag Rate",
            value=f"{fraud_rate:.2f}%", formula="(Fraudulent Transactions / Total) * 100", source=f"`{fraud_col}`",
            warnings="High fraud rate - Review" if fraud_rate > 5 else "None"
        ))
        
        if amount_col is not None:
            fraudulent_amount = amount_series[fraud_mask].sum()
            total_amount = amount_series.sum()
            fraud_revenue_share = (fraudulent_amount / total_amount * 100) if total_amount > 0 else 0
            high_value_fraud_pct = ((fraud_mask & (amount_series >= amount_series.quantile(0.9))).sum() / len(df) * 100) if len(df) > 0 else 0
            
            kpis.append(engine.build_kpi(
                category="🛡️ Fraud Analysis", name="Fraud Revenue Share",
                value=f"{fraud_revenue_share:.2f}%", formula="(Fraudulent $ / Total $) * 100", source=f"`{fraud_col}`, `{amount_col}`",
                warnings="Significant fraud $ impact" if fraud_revenue_share > 2 else "None"
            ))
            kpis.append(engine.build_kpi(
                category="🛡️ Fraud Analysis", name="High-Value Fraud (Top 10%)",
                value=f"{high_value_fraud_pct:.2f}%", formula="(Fraud in Top 10% by $ / Total) * 100", source=f"`{fraud_col}`, `{amount_col}`",
                warnings="Critical: Fraud in high-value transactions" if high_value_fraud_pct > 3 else "None"
            ))
        else:
            kpis.append(engine.log_missing("🛡️ Fraud Analysis", "Fraud Value", "Missing transaction amount."))
    else:
        kpis.append(engine.log_missing("🛡️ Fraud Analysis", "Fraud Metrics", "Missing 'fraud_flag' column."))
        
    if payment_col is not None and fraud_col is not None:
        fraud_attempts = payment_series[fraud_mask]
        if len(fraud_attempts) > 0:
            avg_fraud_attempts = fraud_attempts.mean()
            kpis.append(engine.build_kpi(
                category="🛡️ Fraud Analysis", name="Avg Payment Attempts (Fraudulent)",
                value=f"{avg_fraud_attempts:.2f}", formula="Mean(Attempts in Fraud Cases)", source=f"`{payment_col}`",
                warnings="Multiple retry attempts indicator" if avg_fraud_attempts > 3 else "None"
            ))
    else:
        kpis.append(engine.log_missing("🛡️ Fraud Analysis", "Payment Attempts", "Missing payment attempt data."))
        
    return kpis
