"""
Preventive maintenance, MTBF, MTTR, and maintenance performance metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_maintenance_metrics(df, enable_debug=False):
    """
    Calculates maintenance performance KPIs with optional execution tracing.
    
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
    
    # MTBF and MTTR are ELAPSED TIME (hours between failures, time to repair)
    mtbf_col, mtbf_series = engine.get_numeric(["mtbf_hours", "mean_time_between_failures", "hours_between_failures"])
    mttr_col, mttr_series = engine.get_numeric(["mttr_hours", "mean_time_to_repair", "repair_time"])
    pm_col, pm_series = engine.get_numeric(["preventive_maintenance_hours", "planned_maintenance_hours", "pm_hours"])
    machine_col, machine_series = engine.get_column(["machine_id", "equipment_id", "asset_id"])
    
    # ==========================================
    # 1. MTBF (Mean Time Between Failures)
    # ==========================================
    if mtbf_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        mtbf_clean = mtbf_series.dropna()
        
        if len(mtbf_clean) > 0:
            is_valid, reason = engine.validate_business_rule("duration", mtbf_clean)
            
            if is_valid:
                avg_mtbf = mtbf_clean.mean()
                min_mtbf = mtbf_clean.min()
                
                kpis.append(engine.build_kpi(
                    category="🛠️ Maintenance",
                    name="Avg MTBF (Mean Time Between Failures)",
                    value=f"{avg_mtbf:,.1f} hours",
                    formula="Mean(MTBF)",
                    source=f"`{mtbf_col}`",
                    warnings="Low MTBF - Frequent failures (<100 hrs)" if avg_mtbf < 100 else "None"
                ))
                
                kpis.append(engine.build_kpi(
                    category="🛠️ Maintenance",
                    name="Min MTBF (Weakest Equipment)",
                    value=f"{min_mtbf:,.1f} hours",
                    formula="Min(MTBF)",
                    source=f"`{mtbf_col}`",
                    warnings="Critical: Very low MTBF (<50 hrs)" if min_mtbf < 50 else "None"
                ))
            else:
                kpis.append(engine.log_missing("🛠️ Maintenance", "MTBF", f"Invalid duration: {reason}"))
        else:
            kpis.append(engine.log_missing("🛠️ Maintenance", "MTBF", "All MTBF entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🛠️ Maintenance", "MTBF", "Missing numeric 'mtbf_hours' column."))
    
    # ==========================================
    # 2. MTTR (Mean Time To Repair)
    # ==========================================
    if mttr_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        mttr_clean = mttr_series.dropna()
        
        if len(mttr_clean) > 0:
            is_valid, reason = engine.validate_business_rule("duration", mttr_clean)
            
            if is_valid:
                avg_mttr = mttr_clean.mean()
                max_mttr = mttr_clean.max()
                
                kpis.append(engine.build_kpi(
                    category="🛠️ Maintenance",
                    name="Avg MTTR (Mean Time To Repair)",
                    value=f"{avg_mttr:.2f} hours",
                    formula="Mean(MTTR)",
                    source=f"`{mttr_col}`",
                    warnings="High MTTR - Slow repairs (>4 hrs)" if avg_mttr > 4 else "None"
                ))
                
                kpis.append(engine.build_kpi(
                    category="🛠️ Maintenance",
                    name="Max MTTR (Longest Repair)",
                    value=f"{max_mttr:.2f} hours",
                    formula="Max(MTTR)",
                    source=f"`{mttr_col}`"
                ))
                
                # ==========================================
                # 3. EQUIPMENT AVAILABILITY (from MTBF/MTTR)
                # ==========================================
                if mtbf_col is not None:
                    mtbf_for_avail = mtbf_series.dropna()
                    
                    if len(mtbf_for_avail) > 0:
                        avg_mtbf = mtbf_for_avail.mean()
                        availability = (avg_mtbf / (avg_mtbf + avg_mttr) * 100) if (avg_mtbf + avg_mttr) > 0 else 0
                        
                        warn_msg = "Low availability (<85%)" if availability < 85 else "None"
                        kpis.append(engine.build_kpi(
                            category="🔧 Equipment Health",
                            name="Equipment Availability (from MTBF/MTTR)",
                            value=f"{availability:.2f}%",
                            formula="MTBF / (MTBF + MTTR) * 100",
                            source=f"`{mtbf_col}`, `{mttr_col}`",
                            warnings=warn_msg
                        ))
            else:
                kpis.append(engine.log_missing("🛠️ Maintenance", "MTTR", f"Invalid duration: {reason}"))
        else:
            kpis.append(engine.log_missing("🛠️ Maintenance", "MTTR", "All MTTR entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🛠️ Maintenance", "MTTR", "Missing numeric 'mttr_hours' column."))
    
    # ==========================================
    # 4. PREVENTIVE MAINTENANCE
    # ==========================================
    if pm_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        pm_clean = pm_series.dropna()
        
        if len(pm_clean) > 0:
            is_valid, reason = engine.validate_business_rule("duration", pm_clean)
            
            if is_valid:
                total_pm = pm_clean.sum()
                
                kpis.append(engine.build_kpi(
                    category="🛠️ Maintenance",
                    name="Total Preventive Maintenance Hours",
                    value=f"{total_pm:,.1f} hours",
                    formula="Sum(PM Hours)",
                    source=f"`{pm_col}`"
                ))
                
                # ==========================================
                # 5. PM vs Corrective Ratio
                # ==========================================
                if mttr_col is not None:
                    mttr_for_ratio = mttr_series.dropna()
                    
                    if len(mttr_for_ratio) > 0:
                        total_corrective = mttr_for_ratio.sum()
                        pm_ratio = (total_pm / (total_pm + total_corrective) * 100) if (total_pm + total_corrective) > 0 else 0
                        
                        warn_msg = "Low PM ratio - Reactive maintenance (<30%)" if pm_ratio < 30 else "None"
                        kpis.append(engine.build_kpi(
                            category="🛠️ Maintenance",
                            name="Preventive vs Corrective Ratio",
                            value=f"{pm_ratio:.2f}% PM",
                            formula="(PM Hours / (PM + Corrective)) * 100",
                            source=f"`{pm_col}`, `{mttr_col}`",
                            warnings=warn_msg
                        ))
            else:
                kpis.append(engine.log_missing("🛠️ Maintenance", "PM", f"Invalid duration: {reason}"))
        else:
            kpis.append(engine.log_missing("🛠️ Maintenance", "PM", "All PM entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🛠️ Maintenance", "PM", "Missing numeric 'preventive_maintenance_hours' column."))
    
    # ==========================================
    # 6. MAINTENANCE BY MACHINE
    # ==========================================
    if machine_col is not None and mttr_col is not None:
        machine_mttr = df.groupby(machine_col)[mttr_col].mean().sort_values(ascending=False)
        
        if len(machine_mttr) > 0:
            slowest_machine = machine_mttr.idxmax()
            slowest_mttr = machine_mttr.max()
            
            kpis.append(engine.build_kpi(
                category="🛠️ Maintenance",
                name="Slowest to Repair (Avg MTTR)",
                value=f"{slowest_machine} ({slowest_mttr:.2f} hrs)",
                formula="Machine with max avg MTTR",
                source=f"`{machine_col}`, `{mttr_col}`"
            ))
        else:
            kpis.append(engine.log_missing("🛠️ Maintenance", "Top Machine", "No valid machine data."))
    else:
        kpis.append(engine.log_missing("🛠️ Maintenance", "Top Machine", "Missing 'machine_id' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
