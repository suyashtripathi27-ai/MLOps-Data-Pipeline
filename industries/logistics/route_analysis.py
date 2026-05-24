"""
Route efficiency, distance optimization, and deviation metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_route_efficiency(df):
    """Calculates route optimization and efficiency KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Distance is NOT time - use numeric validation
    actual_dist_col = first_column(df, ["actual_distance", "actual_distance_to_destination", "distance_traveled"])
    planned_dist_col = first_column(df, ["planned_distance", "osrm_distance", "optimal_distance"])
    routing_factor_col = first_column(df, ["routing_factor", "factor", "efficiency_ratio"])
    
    if not actual_dist_col or not planned_dist_col:
        return kpis
    
    # Distances are numeric (miles/km), not time
    if not pd.api.types.is_numeric_dtype(df[actual_dist_col]) or not pd.api.types.is_numeric_dtype(df[planned_dist_col]):
        kpis.append(safe_kpi(
            category="🗺️ Route Efficiency",
            name="Route Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{actual_dist_col}`, `{planned_dist_col}`",
            confidence="Low",
            warnings="Distance columns contain non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [actual_dist_col, planned_dist_col])
    
    actual_dist = df[actual_dist_col].sum()
    planned_dist = df[planned_dist_col].sum()
    
    # Route deviation
    if planned_dist > 0:
        deviation = ((actual_dist - planned_dist) / planned_dist) * 100
        
        kpis.append(safe_kpi(
            category="🗺️ Route Efficiency",
            name="Total Route Deviation %",
            value=f"{deviation:.2f}%",
            formula="((Actual Distance - Planned) / Planned) * 100",
            source=f"`{actual_dist_col}`, `{planned_dist_col}`",
            confidence=conf,
            warnings="High route deviation" if abs(deviation) > 15 else warns
        ))
    
    # Average distances per trip
    avg_actual = actual_dist / len(df) if len(df) > 0 else 0
    avg_planned = planned_dist / len(df) if len(df) > 0 else 0
    
    kpis.append(safe_kpi(
        category="🗺️ Route Efficiency",
        name="Avg Actual Distance (per trip)",
        value=f"{avg_actual:,.2f} km",
        formula="Sum(Actual Distance) / Count(Trips)",
        source=f"`{actual_dist_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="🗺️ Route Efficiency",
        name="Avg Planned Distance (per trip)",
        value=f"{avg_planned:,.2f} km",
        formula="Sum(Planned Distance) / Count(Trips)",
        source=f"`{planned_dist_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Wasted distance
    wasted_distance = (df[actual_dist_col] - df[planned_dist_col]).clip(lower=0).sum()
    
    kpis.append(safe_kpi(
        category="🗺️ Route Efficiency",
        name="Total Wasted Distance",
        value=f"{wasted_distance:,.2f} km",
        formula="Sum(Max(Actual - Planned, 0))",
        source=f"`{actual_dist_col}`, `{planned_dist_col}`",
        confidence=conf,
        warnings="Significant operational waste" if wasted_distance > planned_dist * 0.20 else warns
    ))
    
    # Routing factor (efficiency multiplier)
    if routing_factor_col and pd.api.types.is_numeric_dtype(df[routing_factor_col]):
        valid_factor = df[routing_factor_col].dropna()
        
        if not valid_factor.empty:
            avg_factor = valid_factor.mean()
            
            kpis.append(safe_kpi(
                category="🗺️ Route Efficiency",
                name="Avg Routing Factor",
                value=f"{avg_factor:.2f}x",
                formula="Mean(Actual / Optimal Distance)",
                source=f"`{routing_factor_col}`",
                confidence=conf,
                warnings="Inefficient routing (>1.2x)" if avg_factor > 1.2 else warns
            ))
    
    return kpis


def calc_cost_efficiency(df):
    """Calculates operational cost and efficiency metrics."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Cost and revenue are MONEY, not time
    cost_col = first_column(df, ["total_cost", "operating_cost", "cost_per_km", "fuel_cost"])
    revenue_col = first_column(df, ["revenue", "trip_revenue", "earnings", "gross_revenue"])
    fuel_cost_col = first_column(df, ["fuel_cost", "fuel_expense", "fuel_charges"])
    distance_col = first_column(df, ["distance", "miles](#)*

