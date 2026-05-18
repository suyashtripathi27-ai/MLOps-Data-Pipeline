import pandas as pd
from .reliability import evaluate_kpi_confidence

def calc_iot_sensor_metrics(df):
    """Calculates KPIs for IoT-enabled smart logistics and cold chain tracking."""
    kpis = []
    
    # 1. Cold Chain Risk (Spikes in Temperature)
    if 'temperature_celsius' in df.columns:
        valid_temp = df['temperature_celsius'].dropna()
        if not valid_temp.empty:
            # Assuming cargo requiring climate control shouldn't exceed 25C or go below 0C
            excursions = len(valid_temp[(valid_temp > 25) | (valid_temp < 0)])
            excursion_rate = (excursions / len(valid_temp)) * 100
            
            conf, warns = evaluate_kpi_confidence(df, ['temperature_celsius'])
            kpis.append({
                "category": "🌡️ Cold Chain Quality", "name": "Thermal Excursion Rate",
                "value": f"{excursion_rate:.2f}%", "formula": "(Out-of-Bounds Temp Records / Total Records) * 100",
                "source": "`temperature_celsius`", "confidence": conf, "warnings": warns
            })

    # 2. Asset Capacity Efficiency
    if 'asset_utilization_pct' in df.columns:
        valid_util = df['asset_utilization_pct'].dropna()
        if not valid_util.empty:
            avg_utilization = valid_util.mean()
            
            conf, warns = evaluate_kpi_confidence(df, ['asset_utilization_pct'])
            kpis.append({
                "category": "🚛 Asset Optimization", "name": "Avg Asset Utilization",
                "value": f"{avg_utilization:.1f}%", "formula": "Mean(asset_utilization_pct)",
                "source": "`asset_utilization_pct`", "confidence": conf, "warnings": warns
            })

    # 3. Network Friction (Incident-Based Delay Rate)
    if 'delay_flag' in df.columns:
        valid_delay = df['delay_flag'].dropna()
        if not valid_delay.empty:
            # Handle binary flags (1 for delay, 0 for clear)
            delay_rate = (valid_delay.sum() / len(valid_delay)) * 100
            
            conf, warns = evaluate_kpi_confidence(df, ['delay_flag'])
            kpis.append({
                "category": "🚨 Operational Risk", "name": "Logistics Delay Rate",
                "value": f"{delay_rate:.1f}%", "formula": "(Sum(delay_flag) / Total Trips) * 100",
                "source": "`delay_flag`", "confidence": conf, "warnings": warns
            })
            
    return kpis
