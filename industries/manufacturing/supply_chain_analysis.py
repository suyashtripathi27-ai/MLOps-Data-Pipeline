"""
Supply chain, procurement, and supplier metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_supply_chain_metrics(df):
    """Calculates supply chain and procurement KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Supplier metrics
    supplier_col = first_column(df, ["supplier_id", "supplier_name", "vendor"])
    order_col = first_column(df, ["order_id", "purchase_order", "po"])
    cost_col = first_column(df, ["purchase_cost", "order_cost", "total_cost"])
    lead_time_col = first_column(df, ["lead_time_days", "supplier_lead_time", "delivery_days"])
    quality_col = first_column(df, ["supplier_quality_score", "quality_rating", "defect_rate"])
    
    if not supplier_col and not cost_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [supplier_col, order_col, cost_col, lead_time_col, quality_col] if col])
    
    # Total suppliers
    if supplier_col:
        total_suppliers = df[supplier_col].nunique()
        
        kpis.append(safe_kpi(
            category="🏭 Supply Chain",
            name="Total Active Suppliers",
            value=f"{total_suppliers}",
            formula="Count(Distinct Suppliers)",
            source=f"`{supplier_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Procurement cost
    if cost_col and pd.api.types.is_numeric_dtype(df[cost_col]):
        total_cost = df[cost_col].sum()
        avg_cost = df[cost_col].mean()
        
        kpis.append(safe_kpi(
            category="💰 Procurement",
            name="Total Procurement Cost",
            value=f"${total_cost:,.2f}",
            formula="Sum(Purchase Cost)",
            source=f"`{cost_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Procurement",
            name="Avg Order Cost",
            value=f"${avg_cost:,.2f}",
            formula="Mean(Order Cost)",
            source=f"`{cost_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Lead time analysis
    if lead_time_col and pd.api.types.is_numeric_dtype(df[lead_time_col]):
        valid_lead = df[lead_time_col].dropna()
        
        if not valid_lead.empty:
            avg_lead_time = valid_lead.mean()
            max_lead_time = valid_lead.max()
            
            kpis.append(safe_kpi(
                category="📅 Supplier Performance",
                name="Avg Supplier Lead Time",
                value=f"{avg_lead_time:.1f} days",
                formula="Mean(Lead Time)",
                source=f"`{lead_time_col}`",
                confidence=conf,
                warnings="Long lead times - Supply chain risk" if avg_lead_time > 30 else warns
            ))
            
            kpis.append(safe_kpi(
                category="📅 Supplier Performance",
                name="Max Lead Time",
                value=f"{max_lead_time:.1f} days",
                formula="Max(Lead Time)",
                source=f"`{lead_time_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Supplier quality
    if quality_col and pd.api.types.is_numeric_dtype(df[quality_col]):
        valid_qual = df[quality_col].dropna()
        
        if not valid_qual.empty:
            avg_qual = valid_qual.mean()
            
            kpis.append(safe_kpi(
                category="📅 Supplier Performance",
                name="Avg Supplier Quality Score",
                value=f"{avg_qual:.2f}%",
                formula="Mean(Quality Rating)",
                source=f"`{quality_col}`",
                confidence=conf,
                warnings="Low supplier quality" if avg_qual < 90 else warns
            ))
    
    # Top supplier
    if supplier_col and cost_col and pd.api.types.is_numeric_dtype(df[cost_col]):
        supplier_spend = df.groupby(supplier_col)[cost_col].sum().sort_values(ascending=False)
        
        if not supplier_spend.empty:
            top_supplier = supplier_spend.idxmax()
            top_spend = supplier_spend.max()
            total_spend = supplier_spend.sum()
            top_pct = (top_spend / total_spend * 100) if total_spend > 0 else 0
            
            kpis.append(safe_kpi(
                category="💰 Procurement",
                name="Top Supplier by Spend",
                value=f"{top_supplier} (${top_spend:,.2f})",
                formula="Supplier with max spend",
                source=f"`{supplier_col}`, `{cost_col}`",
                confidence=conf,
                warnings="High supplier concentration" if top_pct > 30 else warns
            ))
    
    return kpis
