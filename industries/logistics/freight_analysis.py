"""
Freight handling, cargo metrics, and damage analysis.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_freight_metrics(df):
    """Calculates freight and cargo handling KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Weight is numeric (tons/kg), not time
    weight_col = first_column(df, ["freight_weight", "total_weight", "cargo_weight", "weight"])
    damage_col = first_column(df, ["damage_incidents", "damaged_goods", "defect_count", "damage_count"])
    shipment_col = first_column(df, ["shipment_id", "shipment", "cargo_id"])
    damage_cost_col = first_column(df, ["damage_cost", "damage_value", "loss_amount"])
    
    if not weight_col:
        return kpis
    
    # Weight is numeric (mass), not duration
    if not pd.api.types.is_numeric_dtype(df[weight_col]):
        kpis.append(safe_kpi(
            category="📦 Freight & Cargo",
            name="Freight Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{weight_col}`",
            confidence="Low",
            warnings="Weight column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [weight_col, damage_col, shipment_col, damage_cost_col] if col])
    
    # Total tonnage
    total_weight = df[weight_col].sum()
    avg_weight = df[weight_col].mean()
    
    kpis.append(safe_kpi(
        category="📦 Freight & Cargo",
        name="Total Tonnage Handled",
        value=f"{total_weight:,.2f} tons",
        formula="Sum(Weight)",
        source=f"`{weight_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="📦 Freight & Cargo",
        name="Avg Shipment Weight",
        value=f"{avg_weight:,.2f} tons",
        formula="Mean(Weight)",
        source=f"`{weight_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Damage analysis
    if damage_col and pd.api.types.is_numeric_dtype(df[damage_col]):
        total_damages = df[damage_col].sum()
        damage_rate = (total_damages / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="📦 Freight & Cargo",
            name="Freight Damage Rate",
            value=f"{damage_rate:.2f}%",
            formula="(Total Damaged Items / Total Shipments) * 100",
            source=f"`{damage_col}`",
            confidence=conf,
            warnings="High damage rate - Quality issues" if damage_rate > 2 else warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Freight & Cargo",
            name="Total Damaged Items",
            value=f"{total_damages:,}",
            formula="Sum(Damage Count)",
            source=f"`{damage_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Damage cost
    if damage_cost_col and pd.api.types.is_numeric_dtype(df[damage_cost_col]):
        total_damage_cost = df[damage_cost_col].sum()
        avg_damage_cost = df[damage_cost_col].mean()
        
        kpis.append(safe_kpi(
            category="📦 Freight & Cargo",
            name="Total Damage Cost",
            value=f"${total_damage_cost:,.2f}",
            formula="Sum(Damage Cost)",
            source=f"`{damage_cost_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Freight & Cargo",
            name="Avg Damage per Incident",
            value=f"${avg_damage_cost:,.2f}",
            formula="Mean(Damage Cost)",
            source=f"`{damage_cost_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Shipment count
    if shipment_col:
        total_shipments = df[shipment_col].nunique()
        
        kpis.append(safe_kpi(
            category="📦 Freight & Cargo",
            name="Total Shipments",
            value=f"{total_shipments:,}",
            formula="Count(Distinct Shipments)",
            source=f"`{shipment_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Avg weight per shipment
        if weight_col:
            avg_weight_per_shipment = total_weight / total_shipments if total_shipments > 0 else 0
            
            kpis.append(safe_kpi(
                category="📦 Freight & Cargo",
                name="Avg Weight per Shipment",
                value=f"{avg_weight_per_shipment:,.2f} tons",
                formula="Total Weight / Shipment Count",
                source=f"`{weight_col}`, `{shipment_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
