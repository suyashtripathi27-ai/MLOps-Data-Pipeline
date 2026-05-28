"""
Route efficiency, distance optimization, and cost metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

LOGISTICS_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_route_efficiency(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    actual_col, actual_series = engine.get_numeric(["actual_distance", "actual_distance_to_destination", "distance_traveled"])
    planned_col, planned_series = engine.get_numeric(["planned_distance", "osrm_distance", "optimal_distance"])
    
    if actual_col is not None and planned_col is not None:
        dist_df = pd.concat([actual_series, planned_series], axis=1).dropna()
        if len(dist_df) > 0:
            total_actual = dist_df[actual_col].sum()
            total_planned = dist_df[planned_col].sum()
            
            if total_planned > 0:
                deviation = ((total_actual - total_planned) / total_planned) * 100
                wasted = (dist_df[actual_col] - dist_df[planned_col]).clip(lower=0).sum()
                
                kpis.append(engine.build_kpi(
                    category="🗺️ Route Efficiency", name="Total Route Deviation %",
                    value=f"{deviation:.2f}%", formula="((Actual - Planned) / Planned) * 100", 
                    source=f"`{actual_col}`, `{planned_col}`", warnings="High route deviation" if deviation > 15 else "None"
                ))
                kpis.append(engine.build_kpi(
                    category="🗺️ Route Efficiency", name="Total Wasted Distance",
                    value=f"{wasted:,.2f} km", formula="Sum(Max(Actual - Planned, 0))", source=f"`{actual_col}`, `{planned_col}`"
                ))
        else:
            kpis.append(engine.log_missing("🗺️ Route Efficiency", "Deviation", "No valid overlapping distance data."))
    else:
        kpis.append(engine.log_missing("🗺️ Route Efficiency", "Deviation", "Requires both actual and planned distance."))

    if enable_debug: engine.print_execution_log()
    return kpis

def calc_cost_efficiency(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    cost_col, cost_series = engine.get_numeric(["total_cost", "operating_cost", "cost_per_km"])
    revenue_col, revenue_series = engine.get_numeric(["revenue", "trip_revenue", "earnings"])
    dist_col, dist_series = engine.get_numeric(["distance", "miles_traveled", "km_traveled", "actual_distance"])
    
    if cost_col is not None and revenue_col is not None:
        finance_df = pd.concat([cost_series, revenue_series], axis=1).dropna()
        if len(finance_df) > 0:
            total_cost = finance_df[cost_col].sum()
            total_rev = finance_df[revenue_col].sum()
            margin = ((total_rev - total_cost) / total_rev * 100) if total_rev > 0 else 0
            
            kpis.append(engine.build_kpi(
                category="💸 Cost & Efficiency", name="Profit Margin",
                value=f"{margin:.2f}%", formula="((Revenue - Cost) / Revenue) * 100", 
                source=f"`{revenue_col}`, `{cost_col}`", warnings="Low margin" if margin < 10 else "None"
            ))
        else:
            kpis.append(engine.log_missing("💸 Cost & Efficiency", "Margin", "No valid overlapping cost/revenue data."))
    else:
        kpis.append(engine.log_missing("💸 Cost & Efficiency", "Margin", "Requires numeric 'revenue' and 'cost'."))

    if cost_col is not None and dist_col is not None:
        dist_df = pd.concat([cost_series, dist_series], axis=1).dropna()
        if len(dist_df) > 0:
            total_c = dist_df[cost_col].sum()
            total_d = dist_df[dist_col].sum()
            if total_d > 0:
                cost_per_km = total_c / total_d
                kpis.append(engine.build_kpi(
                    category="💸 Cost & Efficiency", name="Cost per Km",
                    value=f"${cost_per_km:,.2f}", formula="Total Cost / Total Distance", source=f"`{cost_col}`, `{dist_col}`"
                ))

    if enable_debug: engine.print_execution_log()
    return kpis
