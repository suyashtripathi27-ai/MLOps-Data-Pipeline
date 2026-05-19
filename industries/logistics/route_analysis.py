import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def calc_route_efficiency(df):
    """Calculates Route KPIs."""
    kpis = []
    if 'actual_distance_to_destination' in df.columns and 'osrm_distance' in df.columns:
        # 🛡️ GATEKEEPER CHECK: Ensure distances aren't highly negative/corrupt
        act_valid, act_reason = SemanticValidator.is_valid_duration(df['actual_distance_to_destination'])
        osrm_valid, osrm_reason = SemanticValidator.is_valid_duration(df['osrm_distance'])
        
        if act_valid and osrm_valid:
            actual_dist = df['actual_distance_to_destination'].sum()
            planned_dist = df['osrm_distance'].sum()
            if planned_dist > 0:
                deviation = ((actual_dist - planned_dist) / planned_dist) * 100
                conf, warns = evaluate_kpi_confidence(df, ['actual_distance_to_destination', 'osrm_distance'])
                kpis.append({
                    "category": "🗺️ Route Efficiency", "name": "Total Route Deviation",
                    "value": f"{deviation:.2f}%", "formula": "((Actual - Planned) / Planned) * 100",
                    "source": "`actual_...`, `osrm_...`", "confidence": conf, "warnings": warns
                })
        else:
            kpis.append({
                "category": "🗺️ Route Efficiency", "name": "Total Route Deviation",
                "value": "EXCLUDED", "formula": "N/A",
                "source": "Multiple", "confidence": "Low", 
                "warnings": f"Actual Dist: {act_reason} | OSRM Dist: {osrm_reason}"
            })
            
    if 'factor' in df.columns:
        is_valid, reason = SemanticValidator.is_valid_duration(df['factor'])
        if is_valid:
            avg_factor = df['factor'].dropna().mean()
            conf, warns = evaluate_kpi_confidence(df, ['factor'])
            if warns == "None": warns = ""
            warns += " Semantic definition ambiguous."
            kpis.append({
                "category": "🗺️ Route Efficiency", "name": "Average Routing Factor",
                "value": f"{avg_factor:.2f}", "formula": "Mean(factor)",
                "source": "`factor`", "confidence": conf, "warnings": warns.strip()
            })
        else:
            kpis.append({
                "category": "🗺️ Route Efficiency", "name": "Average Routing Factor",
                "value": "EXCLUDED", "formula": "N/A",
                "source": "`factor`", "confidence": "Low", "warnings": reason
            })
            
    return kpis

def calc_cost_efficiency(df):
    """Calculates operational waste and cost proxies."""
    kpis = []
    if 'actual_distance_to_destination' in df.columns and 'osrm_distance' in df.columns:
        # 🛡️ GATEKEEPER CHECK
        act_valid, _ = SemanticValidator.is_valid_duration(df['actual_distance_to_destination'])
        osrm_valid, _ = SemanticValidator.is_valid_duration(df['osrm_distance'])
        
        if act_valid and osrm_valid:
            wasted_distance = (df['actual_distance_to_destination'] - df['osrm_distance']).clip(lower=0).sum()
            conf, warns = evaluate_kpi_confidence(df, ['actual_distance_to_destination', 'osrm_distance'])
            kpis.append({
                "category": "💸 Cost & Efficiency", "name": "Average Excess Distance (per trip)",
                "value": f"{(wasted_distance / len(df)):,.2f} units", "formula": "Mean(Actual Dist - OSRM Dist) where Actual > OSRM",
                "source": "`actual...`, `osrm...`", "confidence": conf, "warnings": warns
            })
        else:
            kpis.append({
                "category": "💸 Cost & Efficiency", "name": "Average Excess Distance (per trip)",
                "value": "EXCLUDED", "formula": "N/A",
                "source": "Multiple", "confidence": "Low", "warnings": "Underlying distance data failed validation."
            })
    return kpis
