"""
Equipment efficiency, OEE, and productivity metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_efficiency_metrics(df, enable_debug=False):
    """
    Calculates equipment efficiency and OEE KPIs with optional execution tracing.
    
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
    
    # OEE components are percentages (ratios)
    oee_col, oee_series = engine.get_numeric(["oee", "overall_equipment_effectiveness", "overall_effectiveness"])
    availability_col, availability_series = engine.get_numeric(["availability", "uptime_pct", "uptime_percentage"])
    performance_col, performance_series = engine.get_numeric(["performance", "speed_efficiency", "performance_efficiency"])
    quality_col, quality_series = engine.get_numeric(["quality_score", "quality_rate", "quality_pct"])
    
    # ==========================================
    # 1. OVERALL EQUIPMENT EFFECTIVENESS (OEE)
    # ==========================================
    if oee_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        oee_clean = oee_series.dropna()
        
        if len(oee_clean) > 0:
            avg_oee = oee_clean.mean()
            min_oee = oee_clean.min()
            
            warn_msg = "Low OEE - Significant efficiency losses (<85%)" if avg_oee < 85 else "None"
            kpis.append(engine.build_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Overall Equipment Effectiveness (OEE)",
                value=f"{avg_oee:.2f}%",
                formula="Mean(OEE)",
                source=f"`{oee_col}`",
                warnings=warn_msg
            ))
            
            kpis.append(engine.build_kpi(
                category="⚙️ Equipment Efficiency",
                name="Min OEE",
                value=f"{min_oee:.2f}%",
                formula="Min(OEE)",
                source=f"`{oee_col}`"
            ))
        else:
            kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "OEE", "All OEE entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "OEE", "Missing numeric 'oee' column."))
    
    # ==========================================
    # 2. AVAILABILITY
    # ==========================================
    if availability_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        availability_clean = availability_series.dropna()
        
        if len(availability_clean) > 0:
            avg_avail = availability_clean.mean()
            
            warn_msg = "Low availability - Increase uptime (<85%)" if avg_avail < 85 else "None"
            kpis.append(engine.build_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Equipment Availability",
                value=f"{avg_avail:.2f}%",
                formula="Mean(Availability)",
                source=f"`{availability_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "Availability", "All availability entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "Availability", "Missing 'availability' column."))
    
    # ==========================================
    # 3. PERFORMANCE
    # ==========================================
    if performance_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        performance_clean = performance_series.dropna()
        
        if len(performance_clean) > 0:
            avg_perf = performance_clean.mean()
            
            warn_msg = "Low performance - Optimize settings (<85%)" if avg_perf < 85 else "None"
            kpis.append(engine.build_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Equipment Performance",
                value=f"{avg_perf:.2f}%",
                formula="Mean(Performance)",
                source=f"`{performance_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "Performance", "All performance entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "Performance", "Missing 'performance' column."))
    
    # ==========================================
    # 4. QUALITY SCORE
    # ==========================================
    if quality_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        quality_clean = quality_series.dropna()
        
        if len(quality_clean) > 0:
            avg_qual = quality_clean.mean()
            
            warn_msg = "Low quality - Review process (<95%)" if avg_qual < 95 else "None"
            kpis.append(engine.build_kpi(
                category="⚙️ Equipment Efficiency",
                name="Avg Quality Score",
                value=f"{avg_qual:.2f}%",
                formula="Mean(Quality)",
                source=f"`{quality_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "Quality", "All quality entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⚙️ Equipment Efficiency", "Quality", "Missing 'quality_score' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
