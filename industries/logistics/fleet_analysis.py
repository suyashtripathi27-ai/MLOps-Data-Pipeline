import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def calc_fleet_economics(df):
    """Calculates KPIs specifically for Heavy Fleet and Trucking data."""
    kpis = []
    
    # 1. Fleet Profitability Margin
    if 'revenue' in df.columns and 'total_cost' in df.columns:
        total_rev = df['revenue'].sum()
        total_cost = df['total_cost'].sum()
        margin = ((total_rev - total_cost) / total_rev) * 100 if total_rev > 0 else 0
        
        conf, warns = evaluate_kpi_confidence(df, ['revenue', 'total_cost'])
        kpis.append({
            "category": "💰 Fleet Economics", "name": "Overall Profit Margin",
            "value": f"{margin:.2f}%", "formula": "((Revenue - Cost) / Revenue) * 100",
            "source": "`revenue`, `total_cost`", "confidence": conf, "warnings": warns
        })
        
    # 2. Facility Detention Impact (With NaN Guardrails)
    if 'detention_minutes' in df.columns:
        # Drop NaNs just for this calculation so it doesn't break the math
        valid_detention = df['detention_minutes'].dropna()
        
        if not valid_detention.empty:
            avg_detention = valid_detention.mean()
            high_detention_trips = len(valid_detention[valid_detention > 120])
            
            conf, warns = evaluate_kpi_confidence(df, ['detention_minutes'])
            kpis.append({
                "category": "⏳ Operational Bottlenecks", "name": "Avg Facility Detention",
                "value": f"{avg_detention:.1f} mins", "formula": "Mean(detention_minutes)",
                "source": "`detention_minutes`", "confidence": conf, "warnings": warns
            })
            kpis.append({
                "category": "⏳ Operational Bottlenecks", "name": "Severe Detention Events (>2hr)",
                "value": f"{high_detention_trips:,} trips", "formula": "Count(detention_minutes > 120)",
                "source": "`detention_minutes`", "confidence": conf, "warnings": warns
            })

    # 3. Cargo Damage Risk
    if 'cargo_damage_cost' in df.columns:
        valid_damage = df['cargo_damage_cost'].dropna()
        if not valid_damage.empty:
            damage_events = valid_damage[valid_damage > 0]
            damage_rate = (len(damage_events) / len(df)) * 100
            
            conf, warns = evaluate_kpi_confidence(df, ['cargo_damage_cost'])
            kpis.append({
                "category": "🚨 Risk & Compliance", "name": "Cargo Damage Incident Rate",
                "value": f"{damage_rate:.2f}%", "formula": "(Trips with Damage > 0 / Total Trips) * 100",
                "source": "`cargo_damage_cost`", "confidence": conf, "warnings": warns
            })
        
    return kpis
