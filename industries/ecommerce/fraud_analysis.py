"""
Fraud detection and risk metrics for e-commerce.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
# Moderate thresholds - focus on growth velocity vs strict compliance
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,        # ✅ Moderate - tech platforms have data quality
    "score_deduction_for_warning": 12,  # ✅ Lower penalty - more lenient than banking
    "low_confidence_threshold": 35,     # ✅ Higher threshold = harder to flag "Low"
}

def calc_fraud_metrics(df, enable_debug=False):
    """
    Calculate fraud risk KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    # ✅ OPTION 2: Initialize with ecommerce industry config
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    
    # ✅ OPTION 1: Enable tracing for enterprise observability
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    fraud_col, fraud_series = engine.get_column(["fraud_flag", "is_fraud", "chargeback_flag", "suspicious_flag", "fraud_score"])
    amount_col, amount_series = engine.get_numeric(["order_value", "revenue", "sales", "amount", "transaction_amount"])
    payment_col, payment_series = engine.get_numeric(["payment_attempts", "attempts", "retry_count", "failed_attempts"])
    
    if fraud_col is not None:
        fraud_mask = fraud_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'fraud'])
        fraud_count = fraud_mask.sum()
        fraud_rate = (fraud_count / len(df) * 100) if len(df) > 0 else 0
        warn_msg = "High fraud rate - Review" if fraud_rate > 5 else "None"
        
        kpis.append(engine.build_kpi(
            category="🛡️ Fraud Analysis", name="Fraud Flag Rate",
            value=f"{fraud_rate:.2f}%", formula="(Fraudulent Transactions / Total) * 100", source=f"`{fraud_col}`",
            warnings=warn_msg
        ))
        
        # Fraud revenue share
        if amount_col is not None:
            fraudulent_amount = amount_series[fraud_mask].sum()
            total_amount = amount_series.sum()
            fraud_revenue_share = (fraudulent_amount / total_amount * 100) if total_amount > 0 else 0
            warn_msg = "Significant fraud $ impact" if fraud_revenue_share > 2 else "None"
            
            kpis.append(engine.build_kpi(
                category="🛡️ Fraud Analysis", name="Fraud Revenue Share",
                value=f"{fraud_revenue_share:.2f}%", formula="(Fraudulent $ / Total $) * 100", source=f"`{fraud_col}`, `{amount_col}`",
                warnings=warn_msg
            ))
            
            # High-value fraud
            high_value_threshold = amount_series.quantile(0.9)
            high_value_fraud = fraud_mask & (amount_series >= high_value_threshold)
            high_value_fraud_pct = (high_value_fraud.sum() / len(df) * 100) if len(df) > 0 else 0
            warn_msg = "Critical: Fraud in high-value transactions" if high_value_fraud_pct > 3 else "None"
            
            kpis.append(engine.build_kpi(
                category="🛡️ Fraud Analysis", name="High-Value Fraud (Top 10%)",
                value=f"{high_value_fraud_pct:.2f}%", formula="(Fraud in Top 10% by $ / Total) * 100", source=f"`{fraud_col}`, `{amount_col}`",
                warnings=warn_msg
            ))
        
        # Payment attempts
        if payment_col is not None:
            avg_attempts = payment_series.mean()
            fraud_attempts = payment_series[fraud_mask]
            
            if len(fraud_attempts) > 0:
                avg_fraud_attempts = fraud_attempts.mean()
                warn_msg = "Multiple retry attempts indicator" if avg_fraud_attempts > 3 else "None"
                
                kpis.append(engine.build_kpi(
                    category="🛡️ Fraud Analysis", name="Avg Payment Attempts (Fraudulent)",
                    value=f"{avg_fraud_attempts:.2f}", formula="Mean(Attempts in Fraud Cases)", source=f"`{payment_col}`",
                    warnings=warn_msg
                ))
    else:
        kpis.append(engine.log_missing("🛡️ Fraud Analysis", "Fraud Metrics", "Missing 'fraud_flag' column."))
    
    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
