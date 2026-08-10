"""
Pharmaceutical supply chain, inventory, and distribution metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_supply_chain_metrics(df):
    """Calculates supply chain and inventory KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Supply chain metrics are COUNT (units/batches) or MONEY (cost), not time
    batch_col = first_column(df, ["batch_id", "lot_number", "batch_number"])
    inventory_col = first_column(df, ["inventory_level", "stock_on_hand", "available_qty"])
    lead_time_col = first_column(df, ["lead_time_days", "supplier_lead_time", "procurement_time"])
    supplier_col = first_column(df, ["supplier_id", "supplier_name", "vendor"])
    cost_col = first_column(df, ["procurement_cost", "cost", "supply_cost"])
    
    if not batch_col and not inventory_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [batch_col, inventory_col, lead_time_col, supplier_col, cost_col] if col])
    
    # Total batches
    if batch_col:
        total_batches = df[batch_col].nunique()
        
        kpis.append(safe_kpi(
            category="📦 Supply Chain",
            name="Total Batches in Supply Chain",
            value=f"{total_batches:,}",
            formula="Count(Distinct Batches)",
            source=f"`{batch_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Inventory levels
    if inventory_col and pd.api.types.is_numeric_dtype(df[inventory_col]):
        total_inventory = df[inventory_col].sum()
        avg_inventory = df[inventory_col].mean()
        
        kpis.append(safe_kpi(
            category="📦 Supply Chain",
            name="Total Inventory Units",
            value=f"{total_inventory:,.0f}",
            formula="Sum(Inventory Level)",
            source=f"`{inventory_col}`",
            confidence=conf,
            warnings="High inventory - Capital tied up" if total_inventory > 100000 else warns
        ))
        
        kpis.append(safe_kpi(
            category="📦 Supply Chain",
            name="Avg Inventory per Batch",
            value=f"{avg_inventory:,.0f}",
            formula="Mean(Inventory Level)",
            source=f"`{inventory_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Lead time
    if lead_time_col and pd.api.types.is_numeric_dtype(df[lead_time_col]):
        valid_lead = df[lead_time_col].dropna()
        
        if not valid_lead.empty:
            avg_lead_time = valid_lead.mean()
            max_lead_time = valid_lead.max()
            
            kpis.append(safe_kpi(
                category="📅 Procurement",
                name="Avg Supplier Lead Time",
                value=f"{avg_lead_time:.1f} days",
                formula="Mean(Lead Time)",
                source=f"`{lead_time_col}`",
                confidence=conf,
                warnings="Long lead times - Supply risk" if avg_lead_time > 60 else warns
            ))
            
            kpis.append(safe_kpi(
                category="📅 Procurement",
                name="Max Lead Time",
                value=f"{max_lead_time:.1f} days",
                formula="Max(Lead Time)",
                source=f"`{lead_time_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Suppliers
    if supplier_col:
        total_suppliers = df[supplier_col].nunique()
        
        kpis.append(safe_kpi(
            category="📦 Supply Chain",
            name="Total Active Suppliers",
            value=f"{total_suppliers}",
            formula="Count(Distinct Suppliers)",
            source=f"`{supplier_col}`",
            confidence=conf,
            warnings="Single source risk" if total_suppliers == 1 else warns
        ))
    
    # Procurement cost
    if cost_col and pd.api.types.is_numeric_dtype(df[cost_col]):
        total_cost = df[cost_col].sum()
        avg_cost = df[cost_col].mean()
        
        kpis.append(safe_kpi(
            category="💰 Procurement",
            name="Total Procurement Cost",
            value=f"${total_cost:,.2f}",
            formula="Sum(Procurement Cost)",
            source=f"`{cost_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Procurement",
            name="Avg Procurement Cost",
            value=f"${avg_cost:,.2f}",
            formula="Mean(Procurement Cost)",
            source=f"`{cost_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis

# ==========================================
# COMPATIBILITY ALIAS
# ==========================================
calc_pharma_supply_metrics = calc_supply_chain_metrics
