import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def calc_sla_performance(df):
    """Calculates SLA KPIs and returns them as structured dictionaries."""
    kpis = []
    if 'trip_creation_time' in df.columns and 'od_end_time' in df.columns:
        
        # 🛡️ GATEKEEPER CHECK: Ensure timestamps don't have Epoch Corruption
        start_valid, start_reason = SemanticValidator.is_valid_datetime(pd.to_datetime(df['trip_creation_time'], errors='coerce'))
        end_valid, end_reason = SemanticValidator.is_valid_datetime(pd.to_datetime(df['od_end_time'], errors='coerce'))
        
        if start_valid and end_valid:
            start = pd.to_datetime(df['trip_creation_time'], errors='coerce')
            end = pd.to_datetime(df['od_end_time'], errors='coerce')
            valid_times = (end - start).dropna().dt.total_seconds() / 3600
            
            if not valid_times.empty:
                avg_transit = valid_times.mean()
                conf, warns = evaluate_kpi_confidence(df, ['trip_creation_time', 'od_end_time'])
                kpis.append({
                    "category": "⏱️ SLA & Delivery", "name": "Average Transit Time",
                    "value": f"{avg_transit:.2f} hrs", "formula": "Mean(od_end_time - trip_creation_time)",
                    "source": "`trip_creation_time`, `od_end_time`", "confidence": conf, "warnings": warns
                })
        else:
            kpis.append({
                "category": "⏱️ SLA & Delivery", "name": "Average Transit Time",
                "value": "EXCLUDED", "formula": "N/A",
                "source": "Multiple", "confidence": "Low", 
                "warnings": f"Timestamp corruption. Start: {start_reason} | End: {end_reason}"
            })
            
    if 'is_cutoff' in df.columns:
        valid_data = df['is_cutoff'].dropna()
        if not valid_data.empty:
            is_true = valid_data.astype(str).str.lower().isin(['true', '1', 't', 'yes'])
            cutoff_rate = (is_true.sum() / len(valid_data)) * 100
            conf, warns = evaluate_kpi_confidence(df, ['is_cutoff'])
            kpis.append({
                "category": "⏱️ SLA & Delivery", "name": "Trip Cutoff Rate",
                "value": f"{cutoff_rate:.2f}%", "formula": "(True / Total Valid) * 100",
                "source": "`is_cutoff`", "confidence": conf, "warnings": warns
            })
    return kpis
