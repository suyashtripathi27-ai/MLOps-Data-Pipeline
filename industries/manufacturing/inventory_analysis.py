"""
Inventory management, WIP, and stock metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_inventory_metrics(df):
    """Calculates inventory and WIP KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Inventory is COUNT (quantity), not time
    inventory_col = first_column(df, ["inventory_level", "stock_on_hand", "total_inventory", "wip_units"])
    turnover_col = first_column(df, ["inventory_turnover", "turnover_rate", "turnover_ratio"])
    shortage_col = first_column(df, ["stockout_count", "shortage_units", "material_shortage"])
    # Aging is ELAPSED TIME - days materials have been in inventory
    aging_col = first_column(df, ["inventory_age_days", "wip_age_days", "aging_days", "stock_age"])
    
    if not inventory_col and not turnover_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [inventory_col, turnover_col, shortage_col, aging_col] if col])
    
    # Inventory level
    if inventory_col and pd.api.types.is_numeric_dtype(df[inventory_col]):
        avg_inventory = df[inventory_col].mean()
        max_inventory = df[inventory_col].max()
        min_inventory = df[inventory_col].min()
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Avg Inventory Level",
            value=f"{avg_inventory:,.0f} units",
            formula="Mean(Inventory Level)",
            source=f"`{inventory_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Max Inventory Level",
            value=f"{max_inventory:,.0f} units",
            formula="Max(Inventory Level)",
            source=f"`{inventory_col}`",
            confidence=conf,
            warnings="High inventory - Excess capital tied up" if max_inventory > avg_inventory * 2 else warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Min Inventory Level",
            value=f"{min_inventory:,.0f} units",
            formula="Min(Inventory Level)",
            source=f"`{inventory_col}`",
            confidence=conf,
            warnings="Low safety stock risk" if min_inventory < avg_inventory * 0.2 else warns
        ))
    
    # Inventory turnover
    if turnover_col and pd.api.types.is_numeric_dtype(df[turnover_col]):
        valid_turnover = df[turnover_col].dropna()
        
        if not valid_turnover.empty:
            avg_turnover = valid_turnover.mean()
            
            kpis.append(safe_kpi(
                category="📦 Inventory",
                name="Avg Inventory Turnover",
                value=f"{avg_turnover:.2f}x",
                formula="Mean(Turnover Rate)",
                source=f"`{turnover_col}`",
                confidence=conf,
                warnings="Low turnover - Slow moving stock" if avg_turnover < 2 else warns
            ))
    
    # Stockout metrics
    if shortage_col and pd.api.types.is_numeric_dtype(df[shortage_col]):
        total_shortages = df[shortage_col].sum()
        shortage_events = (df[shortage_col] > 0).sum()
        shortage_rate = (shortage_events / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Total Shortage Units",
            value=f"{total_shortages:,.0f}",
            formula="Sum(Shortage Units)",
            source=f"`{shortage_col}`",
            confidence=conf,
            warnings="High shortage impact on production" if total_shortages > 0 else warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Inventory",
            name="Stockout Event Rate",
            value=f"{shortage_rate:.2f}%",
            formula="(Shortage Events / Total) * 100",
            source=f"`{shortage_col}`",
            confidence=conf,
            warnings="Frequent stockouts - Increase safety stock" if shortage_rate > 5 else warns
        ))
    
    # Inventory aging (⏱️ ELAPSED TIME - days in stock)
    if aging_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[aging_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[aging_col]):
            valid_aging = df[aging_col].dropna()
            
            if not valid_aging.empty:
                avg_aging = valid_aging.mean()
                max_aging = valid_aging.max()
                
                kpis.append(safe_kpi(
                    category="📦 Inventory",
                    name="Avg Inventory Age",
                    value=f"{avg_aging:.1f} days",
                    formula="Mean(Inventory Age)",
                    source=f"`{aging_col}`",
                    confidence=conf,
                    warnings="Excessive aging - Obsolescence risk" if avg_aging > 180 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="📦 Inventory",
                    name="Max Inventory Age",
                    value=f"{max_aging:.1f} days",
                    formula="Max(Inventory Age)",
                    source=f"`{aging_col}`",
                    confidence=conf,
                    warnings="Dead stock - Review disposal strategy" if max_aging > 365 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="📦 Inventory",
                name="Aging Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{aging_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    return kpis
