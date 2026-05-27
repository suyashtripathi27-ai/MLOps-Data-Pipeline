"""
Machine downtime, availability, and equipment health metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_downtime_metrics(df, enable_debug=False):
    """
    Calculates downtime and equipment availability KPIs with optional execution tracing.
    
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
    
    # Downtime is ELAPSED TIME (minutes/hours)
    downtime_col, downtime_series = engine.get_numeric(["downtime_hours", "downtime_minutes", "machine_downtime", "unplanned_downtime"])
    machine_col, machine_series = engine.get_column(["machine_id", "equipment_id", "asset_id"])
    reason_col, reason_series = engine.get_column(["downtime_reason", "failure_reason", "stop_reason"])
    
    # ==========================================
    # 1. DOWNTIME METRICS
    # ==========================================
    if downtime_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        downtime_clean = downtime_series.dropna()
        
        if len(downtime_clean) > 0:
            is_valid, reason = engine.validate_business_rule("duration", downtime_clean)
            
            if is_valid:
                total_downtime = downtime_clean.sum()
                avg_downtime = downtime_clean.mean()
                downtime_events = len(downtime_clean)
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Downtime",
                    name="Total Downtime",
                    value=f"{total_downtime:,.1f} hours",
                    formula="Sum(Downtime)",
                    source=f"`{downtime_col}`",
                    warnings="High total downtime (>100 hrs)" if total_downtime > 100 else "None"
                ))
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Downtime",
                    name="Avg Downtime per Event",
                    value=f"{avg_downtime:.2f} hours",
                    formula="Mean(Downtime)",
                    source=f"`{downtime_col}`"
                ))
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Downtime",
                    name="Total Downtime Events",
                    value=f"{downtime_events:,}",
                    formula="Count(Downtime Records)",
                    source=f"`{downtime_col}`"
                ))
                
                # ==========================================
                # 2. EQUIPMENT AVAILABILITY
                # ==========================================
                operating_hours = 8 * 250  # Assume 8hr shifts, 250 working days/year
                availability = ((operating_hours - total_downtime) / operating_hours * 100) if operating_hours > 0 else 0
                
                warn_msg = "CRITICAL: Availability <80%" if availability < 80 else "Low availability (80-85%)" if availability < 85 else "None"
                kpis.append(engine.build_kpi(
                    category="🔧 Equipment Health",
                    name="Equipment Availability %",
                    value=f"{max(0, availability):.2f}%",
                    formula="(Operating Hours - Downtime) / Operating Hours * 100",
                    source=f"`{downtime_col}`",
                    warnings=warn_msg
                ))
            else:
                kpis.append(engine.log_missing("⏱️ Downtime", "Downtime Metrics", f"Invalid duration: {reason}"))
        else:
            kpis.append(engine.log_missing("⏱️ Downtime", "Downtime Metrics", "All downtime entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⏱️ Downtime", "Downtime Metrics", "Missing numeric 'downtime' column."))
    
    # ==========================================
    # 3. DOWNTIME BY MACHINE
    # ==========================================
    if machine_col is not None and downtime_col is not None:
        machine_downtime = df.groupby(machine_col)[downtime_col].sum().sort_values(ascending=False)
        
        if len(machine_downtime) > 0:
            worst_machine = machine_downtime.idxmax()
            worst_downtime = machine_downtime.max()
            
            kpis.append(engine.build_kpi(
                category="🔧 Equipment Health",
                name="Most Problematic Machine",
                value=f"{worst_machine} ({worst_downtime:,.1f} hrs)",
                formula="Machine with max downtime",
                source=f"`{machine_col}`, `{downtime_col}`"
            ))
        else:
            kpis.append(engine.log_missing("🔧 Equipment Health", "Top Machine", "No valid machine data."))
    else:
        kpis.append(engine.log_missing("🔧 Equipment Health", "Top Machine", "Missing 'machine_id' column."))
    
    # ==========================================
    # 4. DOWNTIME REASON BREAKDOWN
    # ==========================================
    if reason_col is not None:
        reason_dist = reason_series.value_counts().head(3)
        
        if len(reason_dist) > 0:
            top_reason = reason_dist.idxmax()
            
            kpis.append(engine.build_kpi(
                category="⏱️ Downtime",
                name="Top Downtime Reason",
                value=f"{top_reason} ({reason_dist.max()} occurrences)",
                formula="Most frequent downtime reason",
                source=f"`{reason_col}`"
            ))
        else:
            kpis.append(engine.log_missing("⏱️ Downtime", "Top Reason", "No valid reason data."))
    else:
        kpis.append(engine.log_missing("⏱️ Downtime", "Top Reason", "Missing 'downtime_reason' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
