import pandas as pd
from .reliability import evaluate_kpi_confidence

def calc_route_efficiency(df):
    """Calculates Route KPIs."""
    kpis = []
    if 'actual_distance_to_destination' in df.columns and 'osrm_distance' in df.columns:
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
            
    if 'factor' in df.columns:
        avg_factor = df['factor'].dropna().mean()
        conf, warns = evaluate_kpi_confidence(df, ['factor'])
        if warns == "None": warns = ""
        warns += " Semantic definition ambiguous."
        kpis.append({
            "category": "🗺️ Route Efficiency", "name": "Average Routing Factor",
            "value": f"{avg_factor:.2f}", "formula": "Mean(factor)",
            "source": "`factor`", "confidence": conf, "warnings": warns.strip()
        })
    return kpis

def calc_cost_efficiency(df):
    """Calculates operational waste and cost proxies."""
    kpis = []
    if 'actual_distance_to_destination' in df.columns and 'osrm_distance' in df.columns:
        wasted_distance = (df['actual_distance_to_destination'] - df['osrm_distance']).clip(lower=0).sum()
        conf, warns = evaluate_kpi_confidence(df, ['actual_distance_to_destination', 'osrm_distance'])
        kpis.append({
            "category": "💸 Cost & Efficiency", "name": "Average Excess Distance (per trip)",
            "value": f"{(wasted_distance / len(df)):,.2f} units", "formula": "Mean(Actual Dist - OSRM Dist) where Actual > OSRM",
            "source": "`actual...`, `osrm...`", "confidence": conf, "warnings": warns
        })
    return kpis
