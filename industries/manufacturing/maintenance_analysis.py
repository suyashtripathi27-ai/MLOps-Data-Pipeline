"""
Preventive maintenance, MTBF, MTTR, and maintenance performance metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_maintenance_metrics(df):
    """Calculates maintenance performance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # MTBF and MTTR are ELAPSED TIME (hours between failures, time to repair)
    mtbf_col = first_column(df, ["mtbf_hours", "mean_time_between_failures", "hours_between_failures"])
    mttr_col = first_column(df, ["mttr_hours", "mean_time_to_repair", "repair_time"])
    pm_col = first_column(df, ["preventive_maintenance_hours", "planned_maintenance_hours", "pm_hours"])
    machine_col = first_column(df, ["machine_id", "equipment_id", "asset_id"])
    
    if not mtbf_col and not mttr_col and not pm_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [mtbf_col, mttr_col, pm_col, machine_col] if col])
    
    # MTBF (Mean Time Between Failures) - ⏱️ ELAPSED TIME
    if mtbf_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[mtbf_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[mtbf_col]):
            valid_mtbf = df[mtbf_col].dropna()
            
            if not valid_mtbf.empty:
                avg_mtbf = valid_mtbf.mean()
                min_mtbf = valid_mtbf.min()
                
                kpis.append(safe_kpi(
                    category="🛠️ Maintenance",
                    name="Avg MTBF (Mean Time Between Failures)",
                    value=f"{avg_mtbf:,.1f} hours",
                    formula="Mean(MTBF)",
                    source=f"`{mtbf_col}`",
                    confidence=conf,
                    warnings="Low MTBF - Frequent failures" if avg_mtbf < 100 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="🛠️ Maintenance",
                    name="Min MTBF (Weakest Equipment)",
                    value=f"{min_mtbf:,.1f} hours",
                    formula="Min(MTBF)",
                    source=f"`{mtbf_col}`",
                    confidence=conf,
                    warnings="Critical: Very low MTBF" if min_mtbf < 50 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="🛠️ Maintenance",
                name="MTBF Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{mtbf_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # MTTR (Mean Time To Repair) - ⏱️ ELAPSED TIME
    if mttr_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[mttr_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[mttr_col]):
            valid_mttr = df[mttr_col].dropna()
            
            if not valid_mttr.empty:
                avg_mttr = valid_mttr.mean()
                max_mttr = valid_mttr.max()
                
                kpis.append(safe_kpi(
                    category="🛠️ Maintenance",
                    name="Avg MTTR (Mean Time To Repair)",
                    value=f"{avg_mttr:.2f} hours",
                    formula="Mean(MTTR)",
                    source=f"`{mttr_col}`",
                    confidence=conf,
                    warnings="High MTTR - Slow repairs" if avg_mttr > 4 else warns
                ))
                
                kpis.append(safe_kpi(
                    category="🛠️ Maintenance",
                    name="Max MTTR (Longest Repair)",
                    value=f"{max_mttr:.2f} hours",
                    formula="Max(MTTR)",
                    source=f"`{mttr_col}`",
                    confidence=conf,
                    warnings=warns
                ))
                
                # Equipment availability from MTBF/MTTR ratio
                if mtbf_col and pd.api.types.is_numeric_dtype(df[mtbf_col]):
                    valid_mtbf = df[mtbf_col].dropna()
                    
                    if not valid_mtbf.empty:
                        avg_mtbf = valid_mtbf.mean()
                        availability = (avg_mtbf / (avg_mtbf + avg_mttr)) * 100 if (avg_mtbf + avg_mttr) > 0 else 0
                        
                        kpis.append(safe_kpi(
                            category="🔧 Equipment Health",
                            name="Equipment Availability (from MTBF/MTTR)",
                            value=f"{availability:.2f}%",
                            formula="MTBF / (MTBF + MTTR) * 100",
                            source=f"`{mtbf_col}`, `{mttr_col}`",
                            confidence=conf,
                            warnings="Low availability" if availability < 85 else warns
                        ))
        else:
            kpis.append(safe_kpi(
                category="🛠️ Maintenance",
                name="MTTR Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{mttr_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Preventive Maintenance - ⏱️ ELAPSED TIME
    if pm_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[pm_col])
        
        if is_valid and pd.api.types.is_numeric_dtype(df[pm_col]):
            total_pm = df[pm_col].sum()
            
            kpis.append(safe_kpi(
                category="🛠️ Maintenance",
                name="Total Preventive Maintenance Hours",
                value=f"{total_pm:,.1f} hours",
                formula="Sum(PM Hours)",
                source=f"`{pm_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            # PM vs corrective ratio
            if mttr_col and pd.api.types.is_numeric_dtype(df[mttr_col]):
                total_corrective = df[mttr_col].sum()
                pm_ratio = (total_pm / (total_pm + total_corrective) * 100) if (total_pm + total_corrective) > 0 else 0
                
                kpis.append(safe_kpi(
                    category="🛠️ Maintenance",
                    name="Preventive vs Corrective Ratio",
                    value=f"{pm_ratio:.2f}% PM",
                    formula="(PM Hours / (PM + Corrective)) * 100",
                    source=f"`{pm_col}`, `{mttr_col}`",
                    confidence=conf,
                    warnings="Low PM ratio - Reactive maintenance" if pm_ratio < 30 else warns
                ))
        else:
            kpis.append(safe_kpi(
                category="🛠️ Maintenance",
                name="PM Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{pm_col}`",
                confidence="Low",
                warnings=f"Invalid duration: {reason}"
            ))
    
    # Maintenance by machine
    if machine_col and mttr_col and pd.api.types.is_numeric_dtype(df[mttr_col]):
        machine_mttr = df.groupby(machine_col)[mttr_col].mean().sort_values(ascending=False)
        
        if not machine_mttr.empty:
            slowest_machine = machine_mttr.idxmax()
            slowest_mttr = machine_mttr.max()
            
            kpis.append(safe_kpi(
                category="🛠️ Maintenance",
                name="Slowest to Repair (Avg MTTR)",
                value=f"{slowest_machine} ({slowest_mttr:.2f} hrs)",
                formula="Machine with max avg MTTR",
                source=f"`{machine_col}`, `{mttr_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
