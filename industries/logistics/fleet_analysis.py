"""
Freight handling, cargo metrics, and damage analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

LOGISTICS_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_freight_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    weight_col, weight_series = engine.get_numeric(["freight_weight", "total_weight", "cargo_weight", "weight"])
    damage_col, damage_series = engine.get_numeric(["damage_incidents", "damaged_goods", "defect_count", "damage_count"])
    shipment_col, shipment_series = engine.get_column(["shipment_id", "shipment", "cargo_id"])
    damage_cost_col, damage_cost_series = engine.get_numeric(["damage_cost", "damage_value", "loss_amount"])
    
    # Weight Metrics
    if weight_col is not None:
        weight_clean = weight_series.dropna()
        if len(weight_clean) > 0:
            total_weight = weight_clean.sum()
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Total Tonnage Handled",
                value=f"{total_weight:,.2f} tons", formula="Sum(Weight)", source=f"`{weight_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Avg Shipment Weight",
                value=f"{weight_clean.mean():,.2f} tons", formula="Mean(Weight)", source=f"`{weight_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📦 Freight & Cargo", "Weight Metrics", "All weight entries are null."))
    else:
        kpis.append(engine.log_missing("📦 Freight & Cargo", "Weight Metrics", "Missing numeric 'weight' column."))

    # Damage Analysis
    if damage_col is not None:
        damage_clean = damage_series.dropna()
        if len(damage_clean) > 0:
            total_damages = damage_clean.sum()
            damage_rate = (total_damages / len(df) * 100) if len(df) > 0 else 0
            
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Freight Damage Rate",
                value=f"{damage_rate:.2f}%", formula="(Total Damaged / Total Rows) * 100", 
                source=f"`{damage_col}`", warnings="High damage rate" if damage_rate > 2 else "None"
            ))
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Total Damaged Items",
                value=f"{total_damages:,.0f}", formula="Sum(Damage Count)", source=f"`{damage_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📦 Freight & Cargo", "Damage Rate", "All damage entries are null."))
    else:
        kpis.append(engine.log_missing("📦 Freight & Cargo", "Damage Rate", "Missing numeric 'damage_incidents'."))

    # Damage Cost
    if damage_cost_col is not None:
        cost_clean = damage_cost_series.dropna()
        if len(cost_clean) > 0:
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Total Damage Cost",
                value=f"${cost_clean.sum():,.2f}", formula="Sum(Damage Cost)", source=f"`{damage_cost_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Avg Damage per Incident",
                value=f"${cost_clean.mean():,.2f}", formula="Mean(Damage Cost)", source=f"`{damage_cost_col}`"
            ))
    
    # Shipment Count
    if shipment_col is not None:
        kpis.append(engine.build_kpi(
            category="📦 Freight & Cargo", name="Total Shipments",
            value=f"{shipment_series.nunique():,}", formula="Count(Distinct Shipments)", source=f"`{shipment_col}`"
        ))

    if enable_debug: engine.print_execution_log()
    return kpis

# ---------------------------------------------------------
# 🚨 ADDED MISSING FUNCTION HERE
# ---------------------------------------------------------
def calc_fleet_economics(df: pd.DataFrame) -> dict:
    """Calculates basic fleet economics for the logistics payload."""
    try:
        # Check if the necessary columns exist based on our schema inference
        if 'total_cost' in df.columns and 'actual_duration_hours' in df.columns:
            avg_cost = df['total_cost'].mean()
            avg_duration = df['actual_duration_hours'].mean()
            
            return {
                "average_shipment_cost": round(float(avg_cost), 2),
                "average_transit_hours": round(float(avg_duration), 2)
            }
    except Exception as e:
        print(f"⚠️ Fleet economics calc failed: {e}")
        
    return {"status": "Fleet economics data unavailable for this dataset."}
