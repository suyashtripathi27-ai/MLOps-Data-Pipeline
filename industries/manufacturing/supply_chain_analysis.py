"""
Supply chain, vendor performance, and procurement metrics for logistics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

LOGISTICS_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_supply_chain_metrics(df, enable_debug=False):
    """
    Calculates supply chain and vendor performance KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Vendor/Supplier metrics
    vendor_col, vendor_series = engine.get_column(["vendor_id", "vendor_name", "supplier_id", "carrier"])
    shipment_col, shipment_series = engine.get_column(["shipment_id", "order_id", "po_number"])
    cost_col, cost_series = engine.get_numeric(["shipping_cost", "vendor_cost", "freight_cost", "transportation_cost"])
    volume_col, volume_series = engine.get_numeric(["shipment_volume", "weight", "units", "quantity"])
    on_time_col, on_time_series = engine.get_numeric(["on_time_rate", "on_time_delivery", "performance_score"])
    quality_col, quality_series = engine.get_numeric(["quality_rating", "defect_rate", "damage_rate", "vendor_rating"])
    
    # ==========================================
    # 1. TOTAL VENDORS
    # ==========================================
    if vendor_col is not None:
        total_vendors = vendor_series.nunique()
        
        kpis.append(engine.build_kpi(
            category="🏭 Supply Chain",
            name="Total Active Vendors",
            value=f"{total_vendors}",
            formula="Count(Distinct Vendors)",
            source=f"`{vendor_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🏭 Supply Chain", "Vendors", "Missing 'vendor_id' column."))
    
    # ==========================================
    # 2. SHIPPING COST ANALYSIS
    # ==========================================
    if cost_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        cost_clean = cost_series.dropna()
        
        if len(cost_clean) > 0:
            total_cost = cost_clean.sum()
            avg_cost = cost_clean.mean()
            max_cost = cost_clean.max()
            min_cost = cost_clean.min()
            
            kpis.append(engine.build_kpi(
                category="💰 Procurement",
                name="Total Shipping Cost",
                value=f"${total_cost:,.2f}",
                formula="Sum(Shipping Cost)",
                source=f"`{cost_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Procurement",
                name="Avg Shipping Cost per Shipment",
                value=f"${avg_cost:,.2f}",
                formula="Mean(Shipping Cost)",
                source=f"`{cost_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Procurement",
                name="Max Shipping Cost",
                value=f"${max_cost:,.2f}",
                formula="Max(Shipping Cost)",
                source=f"`{cost_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="💰 Procurement",
                name="Min Shipping Cost",
                value=f"${min_cost:,.2f}",
                formula="Min(Shipping Cost)",
                source=f"`{cost_col}`"
            ))
        else:
            kpis.append(engine.log_missing("💰 Procurement", "Cost", "All cost entries are missing/null."))
    else:
        kpis.append(engine.log_missing("💰 Procurement", "Cost", "Missing numeric 'shipping_cost' column."))
    
    # ==========================================
    # 3. COST PER VOLUME
    # ==========================================
    if cost_col is not None and volume_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        cost_volume_clean = pd.concat([cost_series, volume_series], axis=1).dropna()
        
        if len(cost_volume_clean) > 0:
            total_cost = cost_volume_clean[cost_col].sum()
            total_volume = cost_volume_clean[volume_col].sum()
            
            if total_volume > 0:
                cost_per_volume = total_cost / total_volume
                
                kpis.append(engine.build_kpi(
                    category="💰 Procurement",
                    name="Cost per Volume Unit",
                    value=f"${cost_per_volume:,.2f}/unit",
                    formula="Total Cost / Total Volume",
                    source=f"`{cost_col}`, `{volume_col}`"
                ))
        else:
            kpis.append(engine.log_missing("💰 Procurement", "Cost per Volume", "Missing valid cost/volume data."))
    else:
        kpis.append(engine.log_missing("💰 Procurement", "Cost per Volume", "Missing 'shipping_cost' or 'volume' column."))
    
    # ==========================================
    # 4. VENDOR PERFORMANCE - ON-TIME DELIVERY
    # ==========================================
    if on_time_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        on_time_clean = on_time_series.dropna()
        
        if len(on_time_clean) > 0:
            avg_on_time = on_time_clean.mean()
            min_on_time = on_time_clean.min()
            
            warn_msg = "Low on-time performance - SLA risk (<95%)" if avg_on_time < 95 else "None"
            kpis.append(engine.build_kpi(
                category="📅 Vendor Performance",
                name="Avg On-Time Delivery Rate",
                value=f"{avg_on_time:.2f}%",
                formula="Mean(On-Time Rate)",
                source=f"`{on_time_col}`",
                warnings=warn_msg
            ))
            
            kpis.append(engine.build_kpi(
                category="📅 Vendor Performance",
                name="Min On-Time Delivery Rate",
                value=f"{min_on_time:.2f}%",
                formula="Min(On-Time Rate)",
                source=f"`{on_time_col}`",
                warnings="Critical: Vendor underperforming (<85%)" if min_on_time < 85 else "None"
            ))
        else:
            kpis.append(engine.log_missing("📅 Vendor Performance", "On-Time", "All on-time entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📅 Vendor Performance", "On-Time", "Missing numeric 'on_time_rate' column."))
    
    # ==========================================
    # 5. VENDOR QUALITY RATING
    # ==========================================
    if quality_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        quality_clean = quality_series.dropna()
        
        if len(quality_clean) > 0:
            avg_quality = quality_clean.mean()
            min_quality = quality_clean.min()
            
            warn_msg = "Low quality rating - Review vendor (<90)" if avg_quality < 90 else "None"
            kpis.append(engine.build_kpi(
                category="📅 Vendor Performance",
                name="Avg Vendor Quality Rating",
                value=f"{avg_quality:.2f}",
                formula="Mean(Quality Rating)",
                source=f"`{quality_col}`",
                warnings=warn_msg
            ))
            
            kpis.append(engine.build_kpi(
                category="📅 Vendor Performance",
                name="Min Vendor Quality Rating",
                value=f"{min_quality:.2f}",
                formula="Min(Quality Rating)",
                source=f"`{quality_col}`",
                warnings="Critical: Vendor quality issue (<75)" if min_quality < 75 else "None"
            ))
        else:
            kpis.append(engine.log_missing("📅 Vendor Performance", "Quality", "All quality entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📅 Vendor Performance", "Quality", "Missing numeric 'quality_rating' column."))
    
    # ==========================================
    # 6. TOP VENDOR BY VOLUME
    # ==========================================
    if vendor_col is not None and volume_col is not None:
        vendor_volume = df.groupby(vendor_col)[volume_col].sum().sort_values(ascending=False)
        
        if len(vendor_volume) > 0:
            top_vendor = vendor_volume.idxmax()
            top_volume = vendor_volume.max()
            total_volume = vendor_volume.sum()
            
            if total_volume > 0:
                top_pct = (top_volume / total_volume * 100)
            else:
                top_pct = 0
            
            warn_msg = "High vendor concentration risk (>40%)" if top_pct > 40 else "None"
            kpis.append(engine.build_kpi(
                category="🏭 Supply Chain",
                name="Top Vendor by Volume",
                value=f"{top_vendor} ({top_volume:,.0f} units, {top_pct:.1f}%)",
                formula="Vendor with max volume",
                source=f"`{vendor_col}`, `{volume_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("🏭 Supply Chain", "Top Vendor", "No valid vendor data."))
    else:
        kpis.append(engine.log_missing("🏭 Supply Chain", "Top Vendor", "Missing 'vendor_id' or 'volume' column."))
    
    # ==========================================
    # 7. TOP VENDOR BY COST
    # ==========================================
    if vendor_col is not None and cost_col is not None:
        vendor_cost = df.groupby(vendor_col)[cost_col].sum().sort_values(ascending=False)
        
        if len(vendor_cost) > 0:
            top_vendor_cost = vendor_cost.idxmax()
            top_cost_amount = vendor_cost.max()
            total_cost = vendor_cost.sum()
            
            if total_cost > 0:
                top_cost_pct = (top_cost_amount / total_cost * 100)
            else:
                top_cost_pct = 0
            
            kpis.append(engine.build_kpi(
                category="💰 Procurement",
                name="Top Vendor by Cost",
                value=f"{top_vendor_cost} (${top_cost_amount:,.2f}, {top_cost_pct:.1f}%)",
                formula="Vendor with max cost",
                source=f"`{vendor_col}`, `{cost_col}`"
            ))
        else:
            kpis.append(engine.log_missing("💰 Procurement", "Top Vendor Cost", "No valid vendor data."))
    else:
        kpis.append(engine.log_missing("💰 Procurement", "Top Vendor Cost", "Missing 'vendor_id' or 'cost' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
