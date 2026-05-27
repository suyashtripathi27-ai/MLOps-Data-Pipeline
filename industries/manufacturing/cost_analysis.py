"""
Manufacturing cost, cost per unit, and cost structure metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_cost_metrics(df, enable_debug=False):
    """
    Calculates manufacturing cost KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    engine = KPIEngine(df, industry_config=MANUFACTURING_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Cost is MONEY, not time
    total_cost_col, total_cost_series = engine.get_numeric(["total_cost", "manufacturing_cost", "production_cost", "cost"])
    labor_col, labor_series = engine.get_numeric(["labor_cost", "wages", "personnel_cost"])
    material_col, material_series = engine.get_numeric(["material_cost", "raw_material_cost", "cogs"])
    overhead_col, overhead_series = engine.get_numeric(["overhead_cost", "indirect_cost", "facility_cost"])
    units_col, units_series = engine.get_numeric(["units_produced", "output", "production_volume"])
    
    # ==========================================
    # 1. TOTAL COST METRICS
    # ==========================================
    if total_cost_col is not None:
        total_cost = total_cost_series.sum()
        avg_cost = total_cost_series.mean()
        
        kpis.append(engine.build_kpi(
            category="💰 Manufacturing Cost",
            name="Total Manufacturing Cost",
            value=f"${total_cost:,.2f}",
            formula="Sum(Cost)",
            source=f"`{total_cost_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="💰 Manufacturing Cost",
            name="Avg Cost per Production Run",
            value=f"${avg_cost:,.2f}",
            formula="Mean(Cost)",
            source=f"`{total_cost_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💰 Manufacturing Cost", "Cost Metrics", "Missing numeric 'total_cost'."))
    
    # ==========================================
    # 2. COST PER UNIT
    # ==========================================
    if total_cost_col is not None and units_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        cost_units_clean = pd.concat([total_cost_series, units_series], axis=1).dropna()
        
        if len(cost_units_clean) > 0:
            total_cost = cost_units_clean[total_cost_col].sum()
            total_units = cost_units_clean[units_col].sum()
            
            if total_units > 0:
                cost_per_unit = total_cost / total_units
                
                kpis.append(engine.build_kpi(
                    category="💰 Manufacturing Cost",
                    name="Cost per Unit",
                    value=f"${cost_per_unit:,.2f}",
                    formula="Total Cost / Total Units",
                    source=f"`{total_cost_col}`, `{units_col}`"
                ))
        else:
            kpis.append(engine.log_missing("💰 Manufacturing Cost", "Cost per Unit", "Missing valid cost/units data."))
    else:
        kpis.append(engine.log_missing("💰 Manufacturing Cost", "Cost per Unit", "Missing 'total_cost' or 'units_produced'."))
    
    # ==========================================
    # 3. LABOR COST ANALYSIS
    # ==========================================
    if labor_col is not None and total_cost_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        labor_clean = pd.concat([labor_series, total_cost_series], axis=1).dropna()
        
        if len(labor_clean) > 0:
            total_labor = labor_clean[labor_col].sum()
            total_cost = labor_clean[total_cost_col].sum()
            
            if total_cost > 0:
                labor_pct = (total_labor / total_cost * 100)
            else:
                labor_pct = 0
            
            kpis.append(engine.build_kpi(
                category="💰 Manufacturing Cost",
                name="Total Labor Cost",
                value=f"${total_labor:,.2f}",
                formula="Sum(Labor Cost)",
                source=f"`{labor_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Manufacturing Cost",
                name="Labor as % of Total Cost",
                value=f"{labor_pct:.2f}%",
                formula="(Labor Cost / Total Cost) * 100",
                source=f"`{labor_col}`, `{total_cost_col}`",
                warnings="High labor cost ratio (>40%)" if labor_pct > 40 else "None"
            ))
        else:
            kpis.append(engine.log_missing("💰 Manufacturing Cost", "Labor Cost", "Missing valid labor/cost data."))
    else:
        kpis.append(engine.log_missing("💰 Manufacturing Cost", "Labor Cost", "Missing 'labor_cost' column."))
    
    # ==========================================
    # 4. MATERIAL COST ANALYSIS
    # ==========================================
    if material_col is not None and total_cost_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        material_clean = pd.concat([material_series, total_cost_series], axis=1).dropna()
        
        if len(material_clean) > 0:
            total_material = material_clean[material_col].sum()
            total_cost = material_clean[total_cost_col].sum()
            
            if total_cost > 0:
                material_pct = (total_material / total_cost * 100)
            else:
                material_pct = 0
            
            kpis.append(engine.build_kpi(
                category="💰 Manufacturing Cost",
                name="Total Material Cost",
                value=f"${total_material:,.2f}",
                formula="Sum(Material Cost)",
                source=f"`{material_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Manufacturing Cost",
                name="Material as % of Total Cost",
                value=f"{material_pct:.2f}%",
                formula="(Material Cost / Total Cost) * 100",
                source=f"`{material_col}`, `{total_cost_col}`"
            ))
        else:
            kpis.append(engine.log_missing("💰 Manufacturing Cost", "Material Cost", "Missing valid material/cost data."))
    else:
        kpis.append(engine.log_missing("💰 Manufacturing Cost", "Material Cost", "Missing 'material_cost' column."))
    
    # ==========================================
    # 5. OVERHEAD COST ANALYSIS
    # ==========================================
    if overhead_col is not None and total_cost_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        overhead_clean = pd.concat([overhead_series, total_cost_series], axis=1).dropna()
        
        if len(overhead_clean) > 0:
            total_overhead = overhead_clean[overhead_col].sum()
            total_cost = overhead_clean[total_cost_col].sum()
            
            if total_cost > 0:
                overhead_pct = (total_overhead / total_cost * 100)
            else:
                overhead_pct = 0
            
            kpis.append(engine.build_kpi(
                category="💰 Manufacturing Cost",
                name="Total Overhead Cost",
                value=f"${total_overhead:,.2f}",
                formula="Sum(Overhead Cost)",
                source=f"`{overhead_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Manufacturing Cost",
                name="Overhead as % of Total Cost",
                value=f"{overhead_pct:.2f}%",
                formula="(Overhead Cost / Total Cost) * 100",
                source=f"`{overhead_col}`, `{total_cost_col}`",
                warnings="High overhead burden (>30%)" if overhead_pct > 30 else "None"
            ))
        else:
            kpis.append(engine.log_missing("💰 Manufacturing Cost", "Overhead Cost", "Missing valid overhead/cost data."))
    else:
        kpis.append(engine.log_missing("💰 Manufacturing Cost", "Overhead Cost", "Missing 'overhead_cost' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
