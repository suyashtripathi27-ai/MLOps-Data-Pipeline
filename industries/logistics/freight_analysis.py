import pandas as pd
from .reliability import evaluate_kpi_confidence

def calc_freight_metrics(df):
    """Calculates KPIs specifically for Freight Forwarding and Shipments."""
    kpis = []
    
    # 1. Cost Efficiency (Cost per Weight Unit)
    if 'total_cost' in df.columns and 'total_weight' in df.columns:
        valid_data = df.dropna(subset=['total_cost', 'total_weight'])
        if not valid_data.empty and valid_data['total_weight'].sum() > 0:
            cost_per_unit = valid_data['total_cost'].sum() / valid_data['total_weight'].sum()
            
            conf, warns = evaluate_kpi_confidence(df, ['total_cost', 'total_weight'])
            kpis.append({
                "category": "📦 Freight Economics", "name": "Cost per Mass Unit",
                "value": f"${cost_per_unit:.2f}", "formula": "Sum(total_cost) / Sum(total_weight)",
                "source": "`total_cost`, `total_weight`", "confidence": conf, "warnings": warns
            })

    # 2. Network Speed (Average Transit Days)
    if 'actual_duration_hours' in df.columns:
        valid_duration = df['actual_duration_hours'].dropna()
        if not valid_duration.empty:
            avg_transit = valid_duration.mean()
            
            conf, warns = evaluate_kpi_confidence(df, ['actual_duration_hours'])
            kpis.append({
                "category": "⚡ Network Velocity", "name": "Average Transit Time",
                "value": f"{avg_transit:.1f} days", "formula": "Mean(actual_duration_hours)",
                "source": "`actual_duration_hours`", "confidence": conf, "warnings": warns
            })

    # 3. Carrier Distance Economics
    if 'total_cost' in df.columns and 'distance_miles' in df.columns:
        valid_dist = df.dropna(subset=['total_cost', 'distance_miles'])
        if not valid_dist.empty and valid_dist['distance_miles'].sum() > 0:
            cost_per_mile = valid_dist['total_cost'].sum() / valid_dist['distance_miles'].sum()
            
            conf, warns = evaluate_kpi_confidence(df, ['total_cost', 'distance_miles'])
            kpis.append({
                "category": "🗺️ Routing Efficiency", "name": "Cost per Mile",
                "value": f"${cost_per_mile:.2f}", "formula": "Sum(total_cost) / Sum(distance_miles)",
                "source": "`total_cost`, `distance_miles`", "confidence": conf, "warnings": warns
            })
            
    return kpis
