"""
Manufacturing cost, cost per unit, and cost structure metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_cost_metrics(df):
    """Calculates manufacturing cost KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Cost is MONEY, not time
    total_cost_col = first_column(df, ["total_cost", "manufacturing_cost", "production_cost", "cost"])
    labor_col = first_column(df, ["labor_cost", "wages", "personnel_cost"])
    material_col = first_column(df, ["material_cost", "raw_material_cost", "cogs"])
    overhead_col = first_column(df, ["overhead_cost", "indirect_cost", "facility_cost"])
    units_col = first_column(df, ["units_produced", "output", "production_volume"])
    
    if not total_cost_col:
        return kpis
    
    # Cost is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[total_cost_col]):
        kpis.append(safe_kpi(
            category="💰 Manufacturing Cost",
            name="Cost Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{total_cost_col}`",
            confidence="Low",
            warnings="Cost column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [total_cost_col, labor_col, material_col, overhead_col, units_col] if col])
    
    # Total cost
    total_cost = df[total_cost_col].sum()
    avg_cost = df[total_cost_col].mean()
    
    kpis.append(safe_kpi(
        category="💰 Manufacturing Cost",
        name="Total Manufacturing Cost",
        value=f"${total_cost:,.2f}",
        formula="Sum(Cost)",
        source=f"`{total_cost_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="💰 Manufacturing Cost",
        name="Avg Cost per Production Run",
        value=f"${avg_cost:,.2f}",
        formula="Mean(Cost)",
        source=f"`{total_cost_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Cost per unit
    if units_col and pd.api.types.is_numeric_dtype(df[units_col]):
        total_units = df[units_col].sum()
        
        if total_units > 0:
            cost_per_unit = total_cost / total_units
            
            kpis.append(safe_kpi(
                category="💰 Manufacturing Cost",
                name="Cost per Unit",
                value=f"${cost_per_unit:,.2f}",
                formula="Total Cost / Total Units",
                source=f"`{total_cost_col}`, `{units_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Labor cost analysis
    if labor_col and pd.api.types.is_numeric_dtype(df[labor_col]):
        total_labor = df[labor_col].sum()
        labor_pct = (total_labor / total_cost * 100) if total_cost > 0 else 0
        
        kpis.append(safe_kpi(
            category="💰 Manufacturing Cost",
            name="Total Labor Cost",
            value=f"${total_labor:,.2f}",
            formula="Sum(Labor Cost)",
            source=f"`{labor_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Manufacturing Cost",
            name="Labor as % of Total Cost",
            value=f"{labor_pct:.2f}%",
            formula="(Labor Cost / Total Cost) * 100",
            source=f"`{labor_col}`, `{total_cost_col}`",
            confidence=conf,
            warnings="High labor cost ratio" if labor_pct > 40 else warns
        ))
    
    # Material cost analysis
    if material_col and pd.api.types.is_numeric_dtype(df[material_col]):
        total_material = df[material_col].sum()
        material_pct = (total_material / total_cost * 100) if total_cost > 0 else 0
        
        kpis.append(safe_kpi(
            category="💰 Manufacturing Cost",
            name="Total Material Cost",
            value=f"${total_material:,.2f}",
            formula="Sum(Material Cost)",
            source=f"`{material_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Manufacturing Cost",
            name="Material as % of Total Cost",
            value=f"{material_pct:.2f}%",
            formula="(Material Cost / Total Cost) * 100",
            source=f"`{material_col}`, `{total_cost_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Overhead cost analysis
    if overhead_col and pd.api.types.is_numeric_dtype(df[overhead_col]):
        total_overhead = df[overhead_col].sum()
        overhead_pct = (total_overhead / total_cost * 100) if total_cost > 0 else 0
        
        kpis.append(safe_kpi(
            category="💰 Manufacturing Cost",
            name="Total Overhead Cost",
            value=f"${total_overhead:,.2f}",
            formula="Sum(Overhead Cost)",
            source=f"`{overhead_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Manufacturing Cost",
            name="Overhead as % of Total Cost",
            value=f"{overhead_pct:.2f}%",
            formula="(Overhead Cost / Total Cost) * 100",
            source=f"`{overhead_col}`, `{total_cost_col}`",
            confidence=conf,
            warnings="High overhead burden" if overhead_pct > 30 else warns
        ))
    
    return kpis
