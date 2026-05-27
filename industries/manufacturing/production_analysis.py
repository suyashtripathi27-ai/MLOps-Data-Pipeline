"""
Production output, plan attainment, and throughput metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_production_metrics(df, enable_debug=False):
    """
    Calculates production output and efficiency KPIs with optional execution tracing.
    
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
    
    # Units are COUNT (quantity), not time
    units_col, units_series = engine.get_numeric(["units_produced", "production_volume", "actual_output", "good_units", "output_units"])
    planned_col, planned_series = engine.get_numeric(["planned_output", "target_output", "production_target", "expected_output"])
    cycle_time_col, cycle_time_series = engine.get_numeric(["cycle_time_seconds", "cycle_time_minutes", "process_time"])
    machine_col, machine_series = engine.get_column(["machine_id", "equipment_id", "production_line"])
    
    # ==========================================
    # 1. PRODUCTION VOLUME
    # ==========================================
    if units_col is not None:
        total_units = units_series.sum()
        avg_units = units_series.mean()
        
        kpis.append(engine.build_kpi(
            category="⚙️ Production",
            name="Total Units Produced",
            value=f"{total_units:,.0f}",
            formula="Sum(Units Produced)",
            source=f"`{units_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="⚙️ Production",
            name="Avg Units per Production Run",
            value=f"{avg_units:,.0f}",
            formula="Mean(Units Produced)",
            source=f"`{units_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⚙️ Production", "Production Volume", "Missing numeric 'units_produced'."))
    
    # ==========================================
    # 2. PLAN ATTAINMENT
    # ==========================================
    if units_col is not None and planned_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        plan_clean = pd.concat([units_series, planned_series], axis=1).dropna()
        
        if len(plan_clean) > 0:
            total_units = plan_clean[units_col].sum()
            total_planned = plan_clean[planned_col].sum()
            
            if total_planned > 0:
                attainment = (total_units / total_planned) * 100
                
                kpis.append(engine.build_kpi(
                    category="⚙️ Production",
                    name="Plan Attainment %",
                    value=f"{attainment:.2f}%",
                    formula="(Total Actual / Total Planned) * 100",
                    source=f"`{units_col}`, `{planned_col}`",
                    warnings="Below target (<95%)" if attainment < 95 else "None"
                ))
                
                kpis.append(engine.build_kpi(
                    category="⚙️ Production",
                    name="Total Planned Output",
                    value=f"{total_planned:,.0f}",
                    formula="Sum(Planned Output)",
                    source=f"`{planned_col}`"
                ))
        else:
            kpis.append(engine.log_missing("⚙️ Production", "Plan Attainment", "Missing valid units/planned data."))
    else:
        kpis.append(engine.log_missing("⚙️ Production", "Plan Attainment", "Missing 'planned_output' column."))
    
    # ==========================================
    # 3. CYCLE TIME METRICS
    # ==========================================
    if cycle_time_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        cycle_clean = cycle_time_series.dropna()
        
        if len(cycle_clean) > 0:
            is_valid, reason = engine.validate_business_rule("duration", cycle_clean)
            
            if is_valid:
                avg_cycle = cycle_clean.mean()
                min_cycle = cycle_clean.min()
                max_cycle = cycle_clean.max()
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Cycle Performance",
                    name="Avg Cycle Time",
                    value=f"{avg_cycle:.2f} sec",
                    formula="Mean(Cycle Time)",
                    source=f"`{cycle_time_col}`"
                ))
                
                kpis.append(engine.build_kpi(
                    category="⏱️ Cycle Performance",
                    name="Min Cycle Time",
                    value=f"{min_cycle:.2f} sec",
                    formula="Min(Cycle Time)",
                    source=f"`{cycle_time_col}`"
                ))
                
                warn_msg = "High variance in cycle time" if (max_cycle - min_cycle) > avg_cycle * 0.5 else "None"
                kpis.append(engine.build_kpi(
                    category="⏱️ Cycle Performance",
                    name="Max Cycle Time",
                    value=f"{max_cycle:.2f} sec",
                    formula="Max(Cycle Time)",
                    source=f"`{cycle_time_col}`",
                    warnings=warn_msg
                ))
            else:
                kpis.append(engine.log_missing("⏱️ Cycle Performance", "Cycle Time", f"Invalid duration: {reason}"))
        else:
            kpis.append(engine.log_missing("⏱️ Cycle Performance", "Cycle Time", "All cycle time entries are missing/null."))
    else:
        kpis.append(engine.log_missing("⏱️ Cycle Performance", "Cycle Time", "Missing 'cycle_time' column."))
    
    # ==========================================
    # 4. THROUGHPUT CALCULATION
    # ==========================================
    if units_col is not None and cycle_time_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        throughput_clean = pd.concat([units_series, cycle_time_series], axis=1).dropna()
        
        if len(throughput_clean) > 0:
            total_units = throughput_clean[units_col].sum()
            total_cycle_time = throughput_clean[cycle_time_col].sum()
            
            if total_cycle_time > 0:
                throughput = (total_units / (total_cycle_time / 3600))
                
                kpis.append(engine.build_kpi(
                    category="⚙️ Production",
                    name="Production Throughput",
                    value=f"{throughput:,.0f} units/hour",
                    formula="Sum(Units) / Sum(Cycle Time in hours)",
                    source=f"`{units_col}`, `{cycle_time_col}`"
                ))
        else:
            kpis.append(engine.log_missing("⚙️ Production", "Throughput", "Missing valid units/cycle_time data."))
    else:
        kpis.append(engine.log_missing("⚙️ Production", "Throughput", "Missing 'units' or 'cycle_time' column."))
    
    # ==========================================
    # 5. PRODUCTION BY MACHINE
    # ==========================================
    if machine_col is not None and units_col is not None:
        machine_output = df.groupby(machine_col)[units_col].sum().sort_values(ascending=False)
        
        if len(machine_output) > 0:
            top_machine = machine_output.idxmax()
            top_output = machine_output.max()
            
            kpis.append(engine.build_kpi(
                category="⚙️ Production",
                name="Top Producing Machine",
                value=f"{top_machine} ({top_output:,.0f} units)",
                formula="Machine with max output",
                source=f"`{machine_col}`, `{units_col}`"
            ))
        else:
            kpis.append(engine.log_missing("⚙️ Production", "Top Machine", "No valid machine data."))
    else:
        kpis.append(engine.log_missing("⚙️ Production", "Top Machine", "Missing 'machine_id' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
