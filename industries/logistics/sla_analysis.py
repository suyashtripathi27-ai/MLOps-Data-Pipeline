"""
Service level agreement compliance and delivery performance.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_sla_performance(df):
    """Calculates SLA compliance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    promised_col = first_column(df, ["promised_delivery", "sla_date", "target_delivery"])
    actual_col = first_column(df, ["actual_delivery", "delivered_date", "delivery_date"])
    shipment_col = first_column(df, ["shipment_id", "order_id", "delivery_id"])
    on_time_col = first_column(df, ["on_time_flag", "sla_met", "on_time_delivery"])
    
    if not promised_col or not actual_col:
        return kpis
    
    # Convert to datetime
    promised_dt = pd.to_datetime(df[promised_col], errors="coerce")
    actual_dt = pd.to_datetime(df[actual_col], errors="coerce")
    
    # Validate datetime
    promised_valid, promised_reason = SemanticValidator.is_valid_datetime(promised_dt.dropna())
    actual_valid, actual_reason = SemanticValidator.is_valid_datetime(actual_dt.dropna())
    
    if not (promised_valid and actual_valid):
        kpis.append(safe_kpi(
            category="📅 SLA Performance",
            name="SLA Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{promised_col}`, `{actual_col}`",
            confidence="Low",
            warnings=f"Invalid dates: Promised={promised_reason}, Actual={actual_reason}"
        ))
        return kpis
    
    conf, warns = confidence_for(df, [promised_col, actual_col])
    
    # Calculate delays (⏱️ This is elapsed time - duration between promised and actual)
    delay_df = pd.DataFrame({
        "promised": promised_dt,
        "actual": actual_dt
    }).dropna()
    
    if not delay_df.empty:
        # Delay is duration - validate as such
        delays = (delay_df["actual"] - delay_df["promised"]).dt.total_seconds() / 86400  # Convert to days
        
        is_valid_delay, reason = SemanticValidator.is_valid_duration(delays)
        
        if is_valid_delay:
            on_time = (delays <= 0).sum()
            on_time_rate = (on_time / len(delays) * 100) if len(delays) > 0 else 0
            
            kpis.append(safe_kpi(
                category="📅 SLA Performance",
                name="On-Time Delivery Rate",
                value=f"{on_time_rate:.2f}%",
                formula="(Deliveries <= Promise Date / Total) * 100",
                source=f"`{promised_col}`, `{actual_col}`",
                confidence=conf,
                warnings="SLA failure - Below 95%" if on_time_rate < 95 else warns
            ))
            
            avg_delay = delays.mean()
            max_delay = delays.max()
            
            kpis.append(safe_kpi(
                category="📅 SLA Performance",
                name="Avg Delivery Delay",
                value=f"{avg_delay:.2f} days",
                formula="Mean(Actual - Promised)",
                source=f"`{promised_col}`, `{actual_col}`",
                confidence=conf,
                warnings="High average delay" if avg_delay > 2 else warns
            ))
            
            kpis.append(safe_kpi(
                category="📅 SLA Performance",
                name="Max Delivery Delay",
                value=f"{max_delay:.2f} days",
                formula="Max(Actual - Promised)",
                source=f"`{promised_col}`, `{actual_col}`",
                confidence=conf,
                warnings=warns
            ))
        else:
            kpis.append(safe_kpi(
                category="📅 SLA Performance",
                name="Delay Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{promised_col}`, `{actual_col}`",
                confidence="Low",
                warnings=f"Invalid delay duration: {reason}"
            ))
    
    # SLA met flag
    if on_time_col:
        sla_met_mask = df[on_time_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'met'])
        sla_met_count = sla_met_mask.sum()
        sla_met_rate = (sla_met_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="📅 SLA Performance",
            name="SLA Met Rate",
            value=f"{sla_met_rate:.2f}%",
            formula="(SLA Met / Total) * 100",
            source=f"`{on_time_col}`",
            confidence=conf,
            warnings="SLA compliance below target" if sla_met_rate < 95 else warns
        ))
    
    return kpis
