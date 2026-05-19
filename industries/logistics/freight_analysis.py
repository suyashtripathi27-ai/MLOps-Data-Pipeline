import pandas as pd
from utils.validator import SemanticValidator

def calc_freight_metrics(df):
    """Calculates KPIs specifically for Freight Forwarding and Shipments with strict validation."""
    kpis = []
    
    # 1. Network Speed (Average Transit Time)
    if 'actual_duration_hours' in df.columns:
        # 🛡️ GATEKEEPER CHECK: Is this duration valid?
        is_valid, reason = SemanticValidator.is_valid_duration(df['actual_duration_hours'])
        
        if is_valid:
            valid_duration = df['actual_duration_hours'].dropna()
            if not valid_duration.empty:
                avg_transit = valid_duration.mean()
                kpis.append({
                    "category": "⚡ Network Velocity", "name": "Average Transit Time",
                    "value": f"{avg_transit:.1f} days",
                    "source": "`actual_duration_hours`"
                })
        else:
            # 🚨 REJECTED: Send warning to Technical Appendix
            kpis.append({
                "category": "⚡ Network Velocity", "name": "Average Transit Time",
                "value": "EXCLUDED",
                "source": f"Data rejected: {reason}"
            })

    # 2. Cost Efficiency (Cost per Weight Unit)
    if 'total_cost' in df.columns and 'total_weight' in df.columns:
        # 🛡️ GATEKEEPER CHECK: Are costs and weights valid (no negatives)?
        cost_valid, cost_reason = SemanticValidator.is_valid_duration(df['total_cost'])
        weight_valid, weight_reason = SemanticValidator.is_valid_duration(df['total_weight'])
        
        if cost_valid and weight_valid:
            valid_data = df.dropna(subset=['total_cost', 'total_weight'])
            if not valid_data.empty and valid_data['total_weight'].sum() > 0:
                cost_per_unit = valid_data['total_cost'].sum() / valid_data['total_weight'].sum()
                kpis.append({
                    "category": "📦 Freight Economics", "name": "Cost per Mass Unit",
                    "value": f"${cost_per_unit:.2f}",
                    "source": "`total_cost`, `total_weight`"
                })
        else:
            kpis.append({
                "category": "📦 Freight Economics", "name": "Cost per Mass Unit",
                "value": "EXCLUDED",
                "source": f"Cost: {cost_reason} | Weight: {weight_reason}"
            })

    return kpis
