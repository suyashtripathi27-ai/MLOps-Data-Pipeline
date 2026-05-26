"""
Fraud detection and financial compliance metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_fraud_metrics(df, enable_debug=False):
    """
    Calculate fraud detection KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    
    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    fraud_col, fraud_series = engine.get_column(["fraud_flag", "is_fraud", "fraud_indicator", "flagged"])
    amount_col, amount_series = engine.get_numeric(["transaction_amount", "amount", "value", "transaction_value"])
    anomaly_col, anomaly_series = engine.get_numeric(["anomaly_score", "fraud_score", "risk_score"])
    
    if fraud_col is not None:
        fraud_mask = fraud_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'fraud', 'flagged'])
        fraud_count = fraud_mask.sum()
        fraud_rate = (fraud_count / len(df) * 100) if len(df) > 0 else 0
        
        warn_msg = "CRITICAL: High fraud rate (>1%)" if fraud_rate > 1 else "Elevated fraud rate (>0.5%)" if fraud_rate > 0.5 else "None"
        kpis.append(engine.build_kpi(
            category="🚨 Fraud Detection", name="Fraud Flag Rate %",
            value=f"{fraud_rate:.2f}%", formula="(Fraudulent / Total) * 100", source=f"`{fraud_col}`",
            warnings=warn_msg
        ))
        
        # Fraud dollar impact
        if amount_col is not None:
            fraudulent_amount = amount_series[fraud_mask].sum()
            total_amount = amount_series.sum()
            fraud_dollar_pct = (fraudulent_amount / total_amount * 100) if total_amount > 0 else 0
            
            warn_msg = "CRITICAL: Significant fraud $ impact (>2%)" if fraud_dollar_pct > 2 else "None"
            kpis.append(engine.build_kpi(
                category="🚨 Fraud Detection", name="Fraud Dollar %",
                value=f"{fraud_dollar_pct:.2f}%", formula="(Fraud $ / Total $) * 100", 
                source=f"`{fraud_col}`, `{amount_col}`",
                warnings=warn_msg
            ))
    
    # Anomaly score
    if anomaly_col is not None:
        avg_anomaly = anomaly_series.mean()
        high_anomaly = (anomaly_series > anomaly_series.quantile(0.90)).sum()
        high_anomaly_pct = (high_anomaly / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🚨 Fraud Detection", name="Avg Anomaly Score",
            value=f"{avg_anomaly:.2f}", formula="Mean(Anomaly Score)", source=f"`{anomaly_col}`"
        ))
        
        warn_msg = "High anomaly activity (>20%)" if high_anomaly_pct > 20 else "None"
        kpis.append(engine.build_kpi(
            category="🚨 Fraud Detection", name="High Anomaly Items %",
            value=f"{high_anomaly_pct:.2f}%", formula="(Anomaly > 90th Percentile) / Total * 100", 
            source=f"`{anomaly_col}`",
            warnings=warn_msg
        ))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
