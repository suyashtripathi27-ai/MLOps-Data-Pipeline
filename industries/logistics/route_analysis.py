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
    distance_col = first_column(df, ["distance", "miles_traveled", "km_traveled"])
    
    if not cost_col or not revenue_col:
        return kpis
    
    # Cost and revenue are MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[cost_col]) or not pd.api.types.is_numeric_dtype(df[revenue_col]):
        kpis.append(safe_kpi(
            category="💸 Cost & Efficiency",
            name="Cost Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{cost_col}`, `{revenue_col}`",
            confidence="Low",
            warnings="Cost/Revenue columns contain non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [cost_col, revenue_col, fuel_cost_col, distance_col] if col])
    
    total_cost = df[cost_col].sum()
    total_revenue = df[revenue_col].sum()
    
    # Profit margin
    margin = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
    
    kpis.append(safe_kpi(
        category="💸 Cost & Efficiency",
        name="Profit Margin",
        value=f"{margin:.2f}%",
        formula="((Revenue - Cost) / Revenue) * 100",
        source=f"`{revenue_col}`, `{cost_col}`",
        confidence=conf,
        warnings="Low/negative margin - Review pricing" if margin < 10 else warns
    ))
    
    # Total costs
    kpis.append(safe_kpi(
        category="💸 Cost & Efficiency",
        name="Total Operating Cost",
        value=f"${total_cost:,.2f}",
        formula="Sum(Cost)",
        source=f"`{cost_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="💸 Cost & Efficiency",
        name="Total Revenue",
        value=f"${total_revenue:,.2f}",
        formula="Sum(Revenue)",
        source=f"`{revenue_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Cost per km
    if distance_col and pd.api.types.is_numeric_dtype(df[distance_col]):
        total_distance = df[distance_col].sum()
        
        if total_distance > 0:
            cost_per_km = total_cost / total_distance
            
            kpis.append(safe_kpi(
                category="💸 Cost & Efficiency",
                name="Cost per Km",
                value=f"${cost_per_km:,.2f}",
                formula="Total Cost / Total Distance",
                source=f"`{cost_col}`, `{distance_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Fuel cost analysis
    if fuel_cost_col and pd.api.types.is_numeric_dtype(df[fuel_cost_col]):
        total_fuel = df[fuel_cost_col].sum()
        fuel_pct = (total_fuel / total_cost * 100) if total_cost > 0 else 0
        
        kpis.append(safe_kpi(
            category="💸 Cost & Efficiency",
            name="Total Fuel Cost",
            value=f"${total_fuel:,.2f}",
            formula="Sum(Fuel Cost)",
            source=f"`{fuel_cost_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💸 Cost & Efficiency",
            name="Fuel as % of Total Cost",
            value=f"{fuel_pct:.2f}%",
            formula="(Fuel Cost / Total Cost) * 100",
            source=f"`{fuel_cost_col}`, `{cost_col}`",
            confidence=conf,
            warnings="High fuel cost ratio" if fuel_pct > 40 else warns
        ))
    
    return kpis
