"""
Inventory management, WIP, and stock metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_inventory_metrics(df, enable_debug=False):
    """
    Calculates inventory and WIP KPIs with optional execution tracing.
    
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
    
    # Inventory is COUNT (quantity), not time
    inventory_col, inventory_series = engine.get_numeric(["inventory_level", "stock_on_hand", "total_inventory", "wip_units"])
    turnover_col, turnover_series = engine.get_numeric(["inventory_turnover", "turnover_rate", "turnover_ratio"])
    shortage_col, shortage_series = engine.get_numeric(["stockout_count", "shortage_units", "material_shortage"])
    aging_col, aging_series = engine.get_numeric(["inventory_age_days", "wip_age_days", "aging_days", "stock_age"])
    
    # ==========================================
    # 1. INVENTORY LEVEL
    # ==========================================
    if inventory_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        inventory_clean = inventory_series.dropna()
        
        if len(inventory_clean) > 0:
            avg_inventory = inventory_clean.mean()
            max_inventory = inventory_clean.max()
            min_inventory = inventory_clean.min()
            
            kpis.append(engine.build_kpi(
                category="📦 Inventory",
                name="Avg Inventory Level",
                value=f"{avg_inventory:,.0f} units",
                formula="Mean(Inventory Level)",
                source=f"`{inventory_col}`"
            ))
            
            warn_msg = "High inventory - Excess capital tied up" if max_inventory > avg_inventory * 2 else "None"
            kpis.append(engine.build_kpi(
                category="📦 Inventory",
                name="Max Inventory Level",
                value=f"{max_inventory:,.0f} units",
                formula="Max(Inventory Level)",
                source=f"`{inventory_col}`",
                warnings=warn_msg
            ))
            
            warn_msg = "Low safety stock risk" if min_inventory < avg_inventory * 0.2 else "None"
            kpis.append(engine.build_kpi(
                category="📦 Inventory",
                name="Min Inventory Level",
                value=f"{min_inventory:,.0f} units",
                formula="Min(Inventory Level)",
                source=f"`{inventory_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("📦 Inventory", "Inventory Level", "All inventory entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📦 Inventory", "Inventory Level", "Missing numeric 'inventory_level' column."))
    
    # ==========================================
    # 2. INVENTORY TURNOVER
    # ==========================================
    if turnover_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        turnover_clean = turnover_series.dropna()
        
        if len(turnover_clean) > 0:
            avg_turnover = turnover_clean.mean()
            
            warn_msg = "Low turnover - Slow moving stock (<2x)" if avg_turnover < 2 else "None"
            kpis.append(engine.build_kpi(
                category="📦 Inventory",
                name="Avg Inventory Turnover",
                value=f"{avg_turnover:.2f}x",
                formula="Mean(Turnover Rate)",
                source=f"`{turnover_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("📦 Inventory", "Turnover", "All turnover entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📦 Inventory", "Turnover", "Missing numeric 'inventory_turnover' column."))
    
    # ==========================================
    # 3. STOCKOUT METRICS
    # ==========================================
    if shortage_col is not None:
        # FIX: Drop NaN values BEFORE calculating and use it for both numerator and denominator
        shortage_clean = shortage_series.dropna()
        
        if len(shortage_clean) > 0:
            total_shortages = shortage_clean.sum()
            shortage_events = (shortage_clean > 0).sum()
            shortage_rate = (shortage_events / len(shortage_clean) * 100)
            
            kpis.append(engine.build_kpi(
                category="📦 Inventory",
                name="Total Shortage Units",
                value=f"{total_shortages:,.0f}",
                formula="Sum(Shortage Units)",
                source=f"`{shortage_col}`",
                warnings="High shortage impact on production" if total_shortages > 0 else "None"
            ))
            
            warn_msg = "Frequent stockouts - Increase safety stock (>5%)" if shortage_rate > 5 else "None"
            kpis.append(engine.build_kpi(
                category="📦 Inventory",
                name="Stockout Event Rate",
                value=f"{shortage_rate:.2f}%",
                formula="(Shortage Events / Total Valid) * 100",
                source=f"`{shortage_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("📦 Inventory", "Shortage", "All shortage entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📦 Inventory", "Shortage", "Missing numeric 'shortage_units' column."))
    
    # ==========================================
    # 4. INVENTORY AGING
    # ==========================================
    if aging_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        aging_clean = aging_series.dropna()
        
        if len(aging_clean) > 0:
            is_valid, reason = engine.validate_business_rule("duration", aging_clean)
            
            if is_valid:
                avg_aging = aging_clean.mean()
                max_aging = aging_clean.max()
                
                warn_msg = "Excessive aging - Obsolescence risk (>180 days)" if avg_aging > 180 else "None"
                kpis.append(engine.build_kpi(
                    category="📦 Inventory",
                    name="Avg Inventory Age",
                    value=f"{avg_aging:.1f} days",
                    formula="Mean(Inventory Age)",
                    source=f"`{aging_col}`",
                    warnings=warn_msg
                ))
                
                warn_msg = "Dead stock - Review disposal strategy (>365 days)" if max_aging > 365 else "None"
                kpis.append(engine.build_kpi(
                    category="📦 Inventory",
                    name="Max Inventory Age",
                    value=f"{max_aging:.1f} days",
                    formula="Max(Inventory Age)",
                    source=f"`{aging_col}`",
                    warnings=warn_msg
                ))
            else:
                kpis.append(engine.log_missing("📦 Inventory", "Aging", f"Invalid duration: {reason}"))
        else:
            kpis.append(engine.log_missing("📦 Inventory", "Aging", "All aging entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📦 Inventory", "Aging", "Missing numeric 'inventory_age_days' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
