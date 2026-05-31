"""
Freight handling, cargo metrics, and damage analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

def calc_freight_metrics(df):
    """Calculates freight and cargo handling KPIs."""
    engine = KPIEngine(df)
    kpis = []
    
    if len(df) == 0:
        return kpis
        
    weight_col, weight_series = engine.get_numeric(["freight_weight", "total_weight", "cargo_weight", "weight"])
    damage_col, damage_series = engine.get_numeric(["damage_incidents", "damaged_goods", "defect_count", "damage_count"])
    shipment_col, shipment_series = engine.get_column(["shipment_id", "shipment", "cargo_id"])
    damage_cost_col, damage_cost_series = engine.get_numeric(["damage_cost", "damage_value", "loss_amount"])
    
    # Weight Metrics
    if weight_col is not None:
        weight_clean = weight_series.dropna()
        if len(weight_clean) > 0:
            total_weight = weight_clean.sum()
            avg_weight = weight_clean.mean()
            
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Total Tonnage Handled",
                value=f"{total_weight:,.2f} tons", formula="Sum(Weight)", source=f"`{weight_col}`"
            ))
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Avg Shipment Weight",
                value=f"{avg_weight:,.2f} tons", formula="Mean(Weight)", source=f"`{weight_col}`"
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
        total_shipments = shipment_series.nunique()
        kpis.append(engine.build_kpi(
            category="📦 Freight & Cargo", name="Total Shipments",
            value=f"{total_shipments:,}", formula="Count(Distinct Shipments)", source=f"`{shipment_col}`"
        ))
        
        # Avg weight per shipment
        if weight_col is not None and total_shipments > 0:
            total_weight = weight_series.dropna().sum()
            avg_weight_per_shipment = total_weight / total_shipments
            kpis.append(engine.build_kpi(
                category="📦 Freight & Cargo", name="Avg Weight per Shipment",
                value=f"{avg_weight_per_shipment:,.2f} tons", formula="Total Weight / Shipment Count", source=f"`{weight_col}, {shipment_col}`"
            ))

    return kpis
