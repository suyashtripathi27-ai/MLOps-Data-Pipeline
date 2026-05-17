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

def calc_hub_intelligence(df):
    kpis = []
    if 'source_name' in df.columns and 'actual_time' in df.columns and 'osrm_time' in df.columns:
        df['delay_minutes'] = df['actual_time'] - df['osrm_time']
        
        # 🛠️ THE FIX: If the cleaner turned this into a "Time Object", convert it back to a raw number!
        if pd.api.types.is_timedelta64_dtype(df['delay_minutes']):
            df['delay_minutes'] = df['delay_minutes'].dt.total_seconds() / 60.0
            
        bad_hubs = df[df['delay_minutes'] > 0].groupby('source_name')['delay_minutes'].mean()
        if not bad_hubs.empty:
            worst_hub = bad_hubs.idxmax()
            worst_delay = bad_hubs.max()
            conf, warns = evaluate_kpi_confidence(df, ['source_name', 'actual_time', 'osrm_time'])
            kpis.append({
                "category": "🏢 Hub Intelligence", "name": "Most Congested Hub",
                "value": f"{worst_hub}", "formula": "Max delay grouped by source",
                "source": "`source_name`", "confidence": conf, "warnings": warns
            })
    return kpis

def calc_cost_efficiency(df):
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
