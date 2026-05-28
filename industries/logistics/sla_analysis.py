"""
Service level agreement compliance and delivery performance.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

LOGISTICS_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_sla_performance(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    promise_col, promise_series = engine.get_datetime(["promised_delivery", "sla_date", "target_delivery"])
    actual_col, actual_series = engine.get_datetime(["actual_delivery", "delivered_date", "delivery_date"])
    
    if promise_col is not None and actual_col is not None:
        delay_df = pd.concat([promise_series, actual_series], axis=1).dropna()
        if len(delay_df) > 0:
            delay_df["delay_days"] = (delay_df[actual_col] - delay_df[promise_col]).dt.total_seconds() / 86400
            
            on_time = (delay_df["delay_days"] <= 0).sum()
            on_time_rate = (on_time / len(delay_df)) * 100
            avg_delay = delay_df["delay_days"].mean()
            
            kpis.append(engine.build_kpi(
                category="📅 SLA Performance", name="On-Time Delivery Rate",
                value=f"{on_time_rate:.2f}%", formula="(Deliveries <= Promise Date / Total Valid) * 100", 
                source=f"`{promise_col}`, `{actual_col}`", warnings="SLA failure" if on_time_rate < 95 else "None"
            ))
            kpis.append(engine.build_kpi(
                category="📅 SLA Performance", name="Avg Delivery Delay",
                value=f"{avg_delay:.2f} days", formula="Mean(Actual - Promised)", source=f"`{promise_col}`, `{actual_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📅 SLA Performance", "Delivery Delays", "No valid overlapping delivery dates."))
    else:
        kpis.append(engine.log_missing("📅 SLA Performance", "Delivery Delays", "Requires 'actual_delivery' and 'promised_delivery'."))

    if enable_debug: engine.print_execution_log()
    return kpis
