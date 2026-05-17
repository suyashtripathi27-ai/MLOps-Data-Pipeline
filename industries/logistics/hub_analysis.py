import pandas as pd
from .reliability import evaluate_kpi_confidence

def calc_hub_intelligence(df):
    kpis = []
    
    # 1. Hub Congestion & Validation Gate
    if 'source_name' in df.columns and 'actual_time' in df.columns and 'osrm_time' in df.columns:
        df['delay_minutes'] = df['actual_time'] - df['osrm_time']
        
        if pd.api.types.is_timedelta64_dtype(df['delay_minutes']):
            df['delay_minutes'] = df['delay_minutes'].dt.total_seconds() / 60.0
            
        # 🚨 THE KPI VALIDATION GATE 🚨
        # Only accept delays greater than 0.1 minutes (6 seconds) to filter out epoch corruption
        valid_delays = df[df['delay_minutes'] > 0.1]
        
        if not valid_delays.empty:
            bad_hubs = valid_delays.groupby('source_name')['delay_minutes'].mean()
            worst_hub = bad_hubs.idxmax()
            worst_delay = bad_hubs.max()
            conf, warns = evaluate_kpi_confidence(df, ['source_name', 'actual_time', 'osrm_time'])
            
            kpis.append({
                "category": "🏢 Hub Intelligence", "name": "Most Congested Hub",
                "value": f"{worst_hub} ({worst_delay:.1f} min avg)", "formula": "Max Avg Delay (>0.1m) by Source",
                "source": "`source_name`", "confidence": conf, "warnings": warns
            })
        else:
            kpis.append({
                "category": "🏢 Hub Intelligence", "name": "Most Congested Hub",
                "value": "EXCLUDED", "formula": "N/A",
                "source": "Multiple", "confidence": "Low", 
                "warnings": "Data failed minimum threshold validation (Epoch corruption suspected)."
            })
            
    # 2. Hub Cutoff Concentration
    if 'source_name' in df.columns and 'is_cutoff' in df.columns:
        valid_cutoff = df[['source_name', 'is_cutoff']].dropna()
        if not valid_cutoff.empty:
            is_true = valid_cutoff['is_cutoff'].astype(str).str.lower().isin(['true', '1', 't', 'yes'])
            valid_cutoff['failed_trip'] = is_true
            
            # Find the hub with the highest absolute number of failures
            worst_failure_hub = valid_cutoff.groupby('source_name')['failed_trip'].sum().idxmax()
            failure_count = valid_cutoff.groupby('source_name')['failed_trip'].sum().max()
            
            conf, warns = evaluate_kpi_confidence(df, ['source_name', 'is_cutoff'])
            kpis.append({
                "category": "🏢 Hub Intelligence", "name": "Highest Cutoff Concentration",
                "value": f"{worst_failure_hub} ({failure_count} failures)", "formula": "Count(Cutoff=True) by Source",
                "source": "`source_name`, `is_cutoff`", "confidence": conf, "warnings": warns
            })

    return kpis
