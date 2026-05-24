"""
Production output, plan attainment, and throughput metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_production_metrics(df):
    """Calculates production output and efficiency KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Units are COUNT (quantity), not time
    units_col = first_column(df, ["units_produced", "production_volume", "actual_output", "good_units", "output_units"])
    planned_col = first_column(df, ["planned_output", "target_output", "production_target", "expected_output"])
    cycle_time_col = first_column(df, ["cycle_time_seconds", "cycle_time_minutes", "process_time"])
    machine_col = first_column(df, ["machine_id", "equipment_id", "production_line"])
    
    if not units_col:
        return kpis
    
    # Units are quantities (COUNT), not duration
    if not pd.api.types.is_numeric_dtype(df[units_col]):
        kpis.append(safe_kpi(
            category="⚙️ Production",
            name="Production Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{units_col}`",
            confidence="Low",
            warnings="Units column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [units_col, planned_col, cycle_time_col, machine_col] if col])
    
    # Total units produced
    total_units = df[units_col].sum()
    avg_units = df[units_col].mean()
    
    kpis.append(safe_kpi(
        category="⚙️ Production",
        name="Total Units Produced",
        value=f"{total_units:,.0f}",
        formula="Sum(Units Produced)",
        source=f"`{units_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="⚙️ Production",
        name="Avg Units per Production Run",
        value=f"{avg_units:,.0f}",
        formula="Mean(Units Produced)",
        source=f"`{units_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Plan attainment
    if planned_col and pd.api.types.is_numeric_dtype(df[planned_col]):
        total_planned = df[planned_col].sum()
        
        if total_planned > 0:
            attainment = (total_units / total_planned) * 100
            
            kpis.append(safe_kpi(
                category="⚙️ Production",
                name="Plan Attainment %",
                value=f"{attainment:.2f}%",
                formula="(Total Actual / Total Planned) * 100",
                source=f"`{units_col}`, `{planned_col}`",
                confidence=conf,
                warnings="Below target (< 95%)" if attainment < 95 else warns
            ))
            
            kpis.append(safe_kpi(
                category="⚙️ Production",
                name="Total Planned Output",
                value=f"{total_planned:,.0f}",
                formula="Sum(Planned Output)",
                source=f"`{planned_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Cycle time (⏱️ ELAPSED TIME - use SemanticValidator)
    if cycle_time_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[cycle_time_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[cycle_time_col]):
            valid_cycle = df[cycle_time_col].dropna()
            
            if not valid_cycle.empty:
                avg_cycle = valid_cycle.mean()
                min_cycle = valid_cycle.min()
                max_cycle = valid_cycle.max()
                
                kpis.append(safe_kpi(
                    category="⏱️ Cycle Performance",
                    name="Avg Cycle Time",
                    value=f"{avg_cycle:.2f} sec",
                    formula="Mean(Cycle Time)",
                    source=f"`{cycle_time_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="⏱️ Cycle Performance",
                    name="Min Cycle Time",
                    value=f"{min_cycle:.2f} sec",
                    formula="Min(Cycle Time)",
                    source=f"`{cycle_time_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                kpis.append(safe_kpi(
                    category="⏱️ Cycle Performance",
                    name="Max Cycle Time",
                    value=f"{max_cycle:.2f} sec",
                    formula="Max(Cycle Time)",
                    source=f"`{cycle_time_col}`",
                    confidence=conf,
                    warnings="High variance in cycle time" if (max_cycle - min_cycle) > avg_cycle * 0.5 else warns
                ))
                
                # Throughput calculation
                if units_col and pd.api.types.is_numeric_dtype(df[units_col]):
                    total_cycle_time = valid_cycle.sum()
                    throughput = (total_units / (total_cycle_time / 3600)) if total_cycle_time > 0 else 0
                    
                    kpis.append(safe_kpi(
                        category="⚙️ Production",
                        name="Production Throughput",
                        value=f"{throughput:,.0f} units/hour",
                        formula="Sum(Units) / Sum(Cycle Time in hours)",
                        source=f"`{units_col}`, `{cycle_time_col}`",
                        confidence=conf,
                        warnings=warns
                    ))
        else:
            kpis.append(safe_kpi(
                category="⏱️ Cycle Performance",
                name="Cycle Time Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{cycle_time_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Production by machine
    if machine_col:
        machine_output = df.groupby(machine_col)[units_col].sum().sort_values(ascending=False)
        
        if not machine_output.empty:
            top_machine = machine_output.idxmax()
            top_output = machine_output.max()
            
            kpis.append(safe_kpi(
                category="⚙️ Production",
                name="Top Producing Machine",
                value=f"{top_machine} ({top_output:,.0f} units)",
                formula="Machine with max output",
                source=f"`{machine_col}`, `{units_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
