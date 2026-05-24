"""
Equipment efficiency, OEE, and productivity metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_efficiency_metrics(df):
    """Calculates equipment efficiency and OEE KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # OEE components are percentages (ratios)
    oee_col = first_column(df, ["oee", "overall_equipment_effectiveness", "overall_effectiveness"])
    availability_col = first_column(df, ["availability", "uptime_pct", "uptime_percentage"])
    performance_col = first_column(df, ["performance", "speed_efficiency", "performance_efficiency"])
    quality_col = first_column(df, ["quality_score", "quality_rate", "quality_pct"])
    
    if not oee_col and not availability_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [oee_col, availability_col, performance_col, quality_col] if col])
    
    # OEE
    if oee_col and pd.api.types.is_numeric_dtype(df[oee_col]):
        valid_oee = df[oee_col].dropna()
        
        if not valid_oee.empty:
            avg_oee = valid_oee.mean()
            
            kpis.append(safe_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Overall Equipment Effectiveness (OEE)",
                value=f"{avg_oee:.2f}%",
                formula="Mean(OEE)",
                source=f"`{oee_col}`",
                confidence=conf,
                warnings="Low OEE - Significant efficiency losses" if avg_oee < 85 else "Good OEE" if avg_oee >= 85 else warns
            ))
    
    # Availability
    if availability_col and pd.api.types.is_numeric_dtype(df[availability_col]):
        valid_avail = df[availability_col].dropna()
        
        if not valid_avail.empty:
            avg_avail = valid_avail.mean()
            
            kpis.append(safe_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Equipment Availability",
                value=f"{avg_avail:.2f}%",
                formula="Mean(Availability)",
                source=f"`{availability_col}`",
                confidence=conf,
                warnings="Low availability - Increase uptime" if avg_avail < 85 else warns
            ))
    
    # Performance
    if performance_col and pd.api.types.is_numeric_dtype(df[performance_col]):
        valid_perf = df[performance_col].dropna()
        
        if not valid_perf.empty:
            avg_perf = valid_perf.mean()
            
            kpis.append(safe_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Equipment Performance",
                value=f"{avg_perf:.2f}%",
                formula="Mean(Performance)",
                source=f"`{performance_col}`",
                confidence=conf,
                warnings="Low performance - Optimize settings" if avg_perf < 85 else warns
            ))
    
    # Quality score
    if quality_col and pd.api.types.is_numeric_dtype(df[quality_col]):
        valid_qual = df[quality_col].dropna()
        
        if not valid_qual.empty:
            avg_qual = valid_qual.mean()
            
            kpis.append(safe_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Quality Score",
                value=f"{avg_qual:.2f}%",
                formula="Mean(Quality)",
                source=f"`{quality_col}`",
                confidence=conf,
                warnings="Low quality - Review process" if avg_qual < 95 else warns
            ))
    
    return kpis
