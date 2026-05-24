"""
Fleet utilization, vehicle performance, and detention metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_fleet_economics(df):
    """Calculates fleet performance and economics KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Revenue and cost are MONEY, not time
    vehicle_col = first_column(df, ["vehicle_id", "truck_id", "asset_id", "vehicle_key"])
    revenue_col = first_column(df, ["revenue", "earnings", "trip_revenue", "gross_revenue"])
    cost_col = first_column(df, ["total_cost", "operating_cost", "trip_cost"])
    
    if not revenue_col or not cost_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [vehicle_col, revenue_col, cost_col] if col])
    
    # Fleet size
    if vehicle_col:
        total_vehicles = df[vehicle_col].nunique()
        
        kpis.append(safe_kpi(
            category="🚗 Fleet Management",
            name="Total Fleet Size",
            value=f"{total_vehicles}",
            formula="Count(Distinct Vehicles)",
            source=f"`{vehicle_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Fleet profitability
    if pd.api.types.is_numeric_dtype(df[revenue_col]) and pd.api.types.is_numeric_dtype(df[cost_col]):
        total_revenue = df[revenue_col].sum()
        total_cost = df[cost_col].sum()
        profit = total_revenue - total_cost
        margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        kpis.append(safe_kpi(
            category="💰 Fleet Economics",
            name="Fleet Profit Margin",
            value=f"{margin:.2f}%",
            formula="((Revenue - Cost) / Revenue) * 100",
            source=f"`{revenue_col}`, `{cost_col}`",
            confidence=conf,
            warnings="Low/negative margin" if margin < 10 else warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Fleet Economics",
            name="Total Fleet Revenue",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Fleet Economics",
            name="Total Fleet Cost",
            value=f"${total_cost:,.2f}",
            formula="Sum(Cost)",
            source=f"`{cost_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Detention time (⏱️ ELAPSED TIME - use SemanticValidator)
    detention_col = first_column(df, ["detention_minutes", "detention_hours", "detention_time"])
    if detention_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[detention_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[detention_col]):
            valid_detention = df[detention_col].dropna()
            
            if not valid_detention.empty:
                avg_detention = valid_detention.mean()
                total_detention = valid_detention.sum()
                
                kpis.append(safe_kpi(
                    category="⏳ Detention",
                    name="Avg Facility Detention Time",
                    value=f"{avg_detention:.1f} mins",
                    formula="Mean(Detention Time)",
                    source=f"`{detention_col}`",
                    confidence=conf,
                    warnings="High detention - Optimize processes" if avg_detention > 120 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="⏳ Detention",
                    name="Total Detention Time",
                    value=f"{total_detention:,.0f} mins ({total_detention/60:.0f} hrs)",
                    formula="Sum(Detention Time)",
                    source=f"`{detention_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                # Severe detention events
                severe_detention = (valid_detention > 120).sum()
                severe_pct = (severe_detention / len(valid_detention) * 100) if len(valid_detention) > 0 else 0
                
                kpis.append(safe_kpi(
                    category="⏳ Detention",
                    name="Severe Detention Events (>2hrs)",
                    value=f"{severe_detention:,} ({severe_pct:.2f}%)",
                    formula="Count(Detention > 120 mins)",
                    source=f"`{detention_col}`",
                    confidence=conf,
                    warnings="Critical operational bottleneck" if severe_pct > 20 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="⏳ Detention",
                name="Detention Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{detention_col}`",
                confidence="Low",
                warnings=f"Invalid duration data: {reason}"
            ))
    
    # Cargo damage risk
    damage_col = first_column(df, ["cargo_damage_cost", "damage_cost", "damage_incidents"])
    if damage_col and pd.api.types.is_numeric_dtype(df[damage_col]):
        valid_damage = df[damage_col].dropna()
        
        if not valid_damage.empty:
            damage_events = (valid_damage > 0).sum()
            total_damage = valid_damage.sum()
            damage_rate = (damage_events / len(df) * 100) if len(df) > 0 else 0
            
            kpis.append(safe_kpi(
                category="🚨 Risk & Compliance",
                name="Cargo Damage Rate",
                value=f"{damage_rate:.2f}%",
                formula="(Damage Events / Total Trips) * 100",
                source=f"`{damage_col}`",
                confidence=conf,
                warnings="High damage rate - Quality issues" if damage_rate > 2 else warns
            ))
            
            kpis.append(safe_kpi(
                category="🚨 Risk & Compliance",
                name="Total Damage Cost",
                value=f"${total_damage:,.2f}",
                formula="Sum(Damage Cost)",
                source=f"`{damage_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
