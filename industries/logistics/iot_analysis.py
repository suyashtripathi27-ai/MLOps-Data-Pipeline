"""
IoT sensors, cold chain tracking, and real-time asset monitoring.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

LOGISTICS_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_iot_sensor_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    temp_col, temp_series = engine.get_numeric(["temperature_celsius", "temperature", "temp_c"])
    humid_col, humid_series = engine.get_numeric(["humidity_pct", "humidity", "relative_humidity"])
    util_col, util_series = engine.get_numeric(["asset_utilization_pct", "utilization", "capacity_utilization"])
    delay_col, delay_series = engine.get_column(["delay_flag", "is_delayed", "delayed"])
    
    if temp_col is not None:
        temp_clean = temp_series.dropna()
        if len(temp_clean) > 0:
            out_of_range = ((temp_clean < 2) | (temp_clean > 8)).sum()
            excursion_rate = (out_of_range / len(temp_clean)) * 100
            
            kpis.append(engine.build_kpi(
                category="🌡️ Cold Chain Quality", name="Avg Temperature",
                value=f"{temp_clean.mean():.1f}°C", formula="Mean(Temperature)", source=f"`{temp_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="🌡️ Cold Chain Quality", name="Thermal Excursion Rate",
                value=f"{excursion_rate:.2f}%", formula="(Out-of-Range / Total) * 100", 
                source=f"`{temp_col}`", warnings="Critical cold chain breach" if excursion_rate > 5 else "None"
            ))
        else:
            kpis.append(engine.log_missing("🌡️ Cold Chain Quality", "Temperature", "All temp values are null."))
    else:
        kpis.append(engine.log_missing("🌡️ Cold Chain Quality", "Temperature", "Missing 'temperature' column."))

    if util_col is not None:
        util_clean = util_series.dropna()
        if len(util_clean) > 0:
            avg_util = util_clean.mean()
            underutilized = (util_clean < 50).sum() / len(util_clean) * 100
            
            kpis.append(engine.build_kpi(
                category="🚛 Asset Optimization", name="Avg Asset Utilization",
                value=f"{avg_util:.1f}%", formula="Mean(Utilization)", source=f"`{util_col}`",
                warnings="Low utilization" if avg_util < 50 else "None"
            ))
            kpis.append(engine.build_kpi(
                category="🚛 Asset Optimization", name="Underutilized Assets (<50%)",
                value=f"{underutilized:.2f}%", formula="(Assets < 50% / Total) * 100", source=f"`{util_col}`"
            ))
    
    if delay_col is not None:
        delay_clean = delay_series.dropna().astype(str).str.lower()
        if len(delay_clean) > 0:
            delays = delay_clean.isin(['1', 'true', 'yes', 'delayed']).sum()
            delay_rate = (delays / len(delay_clean)) * 100
            kpis.append(engine.build_kpi(
                category="🚨 Operational Risk", name="Logistics Delay Rate",
                value=f"{delay_rate:.2f}%", formula="(Delayed Trips / Valid Rows) * 100", 
                source=f"`{delay_col}`", warnings="High delay rate" if delay_rate > 15 else "None"
            ))

    if enable_debug: engine.print_execution_log()
    return kpis
