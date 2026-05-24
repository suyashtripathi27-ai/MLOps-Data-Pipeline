"""
IoT sensors, cold chain tracking, and real-time asset monitoring.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_iot_sensor_metrics(df):
    """Calculates IoT and cold chain KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    temp_col = first_column(df, ["temperature_celsius", "temperature", "temp_c"])
    humidity_col = first_column(df, ["humidity_pct", "humidity", "relative_humidity"])
    asset_util_col = first_column(df, ["asset_utilization_pct", "utilization", "capacity_utilization"])
    delay_col = first_column(df, ["delay_flag", "is_delayed", "delayed"])
    exposure_col = first_column(df, ["thermal_exposure_duration", "exposure_minutes", "cold_chain_breach"])
    
    conf, warns = confidence_for(df, [col for col in [temp_col, humidity_col, asset_util_col, delay_col, exposure_col] if col])
    
    # Temperature excursion analysis
    if temp_col and pd.api.types.is_numeric_dtype(df[temp_col]):
        valid_temp = df[temp_col].dropna()
        
        if not valid_temp.empty:
            avg_temp = valid_temp.mean()
            max_temp = valid_temp.max()
            min_temp = valid_temp.min()
            
            # Standard cold chain: 2-8°C for most pharma/perishables
            out_of_range = ((valid_temp < 2) | (valid_temp > 8)).sum()
            excursion_rate = (out_of_range / len(valid_temp) * 100) if len(valid_temp) > 0 else 0
            
            kpis.append(safe_kpi(
                category="🌡️ Cold Chain Quality",
                name="Avg Temperature",
                value=f"{avg_temp:.1f}°C",
                formula="Mean(Temperature)",
                source=f"`{temp_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🌡️ Cold Chain Quality",
                name="Temperature Range",
                value=f"{min_temp:.1f}°C to {max_temp:.1f}°C",
                formula="Min to Max Temperature",
                source=f"`{temp_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="🌡️ Cold Chain Quality",
                name="Thermal Excursion Rate",
                value=f"{excursion_rate:.2f}%",
                formula="(Out-of-Range Readings / Total) * 100",
                source=f"`{temp_col}`",
                confidence=conf,
                warnings="Critical cold chain breach" if excursion_rate > 5 else warns
            ))
    
    # Humidity monitoring
    if humidity_col and pd.api.types.is_numeric_dtype(df[humidity_col]):
        valid_humid = df[humidity_col].dropna()
        
        if not valid_humid.empty:
            avg_humid = valid_humid.mean()
            
            kpis.append(safe_kpi(
                category="💧 Environmental Control",
                name="Avg Humidity",
                value=f"{avg_humid:.1f}%",
                formula="Mean(Humidity)",
                source=f"`{humidity_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Asset utilization
    if asset_util_col and pd.api.types.is_numeric_dtype(df[asset_util_col]):
        valid_util = df[asset_util_col].dropna()
        
        if not valid_util.empty:
            avg_util = valid_util.mean()
            
            kpis.append(safe_kpi(
                category="🚛 Asset Optimization",
                name="Avg Asset Utilization",
                value=f"{avg_util:.1f}%",
                formula="Mean(Utilization %)",
                source=f"`{asset_util_col}`",
                confidence=conf,
                warnings="Low utilization - Optimize fleet" if avg_util < 50 else "Good utilization" if avg_util > 80 else warns
            ))
            
            # Underutilized assets
            underutilized = (valid_util < 50).sum()
            underutil_pct = (underutilized / len(valid_util) * 100) if len(valid_util) > 0 else 0
            
            kpis.append(safe_kpi(
                category="🚛 Asset Optimization",
                name="Underutilized Assets (<50%)",
                value=f"{underutil_pct:.2f}%",
                formula="(Assets < 50% Util / Total) * 100",
                source=f"`{asset_util_col}`",
                confidence=conf,
                warnings="High unutilized capacity" if underutil_pct > 20 else warns
            ))
    
    # Delay detection
    if delay_col:
        delay_mask = df[delay_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'delayed'])
        delay_count = delay_mask.sum()
        delay_rate = (delay_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="🚨 Operational Risk",
            name="Logistics Delay Rate",
            value=f"{delay_rate:.2f}%",
            formula="(Delayed Trips / Total) * 100",
            source=f"`{delay_col}`",
            confidence=conf,
            warnings="High delay rate - SLA risk" if delay_rate > 15 else warns
        ))
    
    # Exposure duration (⏱️ ELAPSED TIME - use SemanticValidator)
    if exposure_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[exposure_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[exposure_col]):
            valid_exposure = df[exposure_col].dropna()
            
            if not valid_exposure.empty:
                avg_exposure = valid_exposure.mean()
                total_exposure = valid_exposure.sum()
                
                kpis.append(safe_kpi(
                    category="🌡️ Cold Chain Quality",
                    name="Avg Thermal Exposure Duration",
                    value=f"{avg_exposure:.1f} mins",
                    formula="Mean(Exposure Time)",
                    source=f"`{exposure_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="🌡️ Cold Chain Quality",
                    name="Total Thermal Exposure",
                    value=f"{total_exposure:,.0f} mins ({total_exposure/60:.0f} hrs)",
                    formula="Sum(Exposure Time)",
                    source=f"`{exposure_col}`",
                    confidence=conf,
                    warnings="Critical: Excessive thermal exposure" if avg_exposure > 60 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="🌡️ Cold Chain Quality",
                name="Thermal Exposure Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{exposure_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    return kpis
