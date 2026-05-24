"""
Machine downtime, availability, and equipment health metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_downtime_metrics(df):
    """Calculates downtime and equipment availability KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Downtime is ELAPSED TIME (minutes/hours)
    downtime_col = first_column(df, ["downtime_hours", "downtime_minutes", "machine_downtime", "unplanned_downtime"])
    machine_col = first_column(df, ["machine_id", "equipment_id", "asset_id"])
    reason_col = first_column(df, ["downtime_reason", "failure_reason", "stop_reason"])
    
    if not downtime_col:
        return kpis
    
    # Validate downtime is elapsed time
    is_valid, reason = SemanticValidator.is_valid_duration(df[downtime_col])
    
    if not is_valid:
        kpis.append(safe_kpi(
            category="⏱️ Downtime",
            name="Downtime Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{downtime_col}`",
            confidence="Low",
            warnings=f"Invalid duration: {reason}"
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [downtime_col, machine_col, reason_col] if col])
    
    if pd.api.types.is_numeric_dtype(df[downtime_col]):
        valid_downtime = df[downtime_col].dropna()
        
        if not valid_downtime.empty:
            total_downtime = valid_downtime.sum()
            avg_downtime = valid_downtime.mean()
            downtime_events = len(valid_downtime)
            
            kpis.append(safe_kpi(
                category="⏱️ Downtime",
                name="Total Downtime",
                value=f"{total_downtime:,.1f} hours",
                formula="Sum(Downtime)",
                source=f"`{downtime_col}`",
                confidence=conf,
                warnings="High total downtime" if total_downtime > 100 else warns
            ))
            
            kpis.append(safe_kpi(
                category="⏱️ Downtime",
                name="Avg Downtime per Event",
                value=f"{avg_downtime:.2f} hours",
                formula="Mean(Downtime)",
                source=f"`{downtime_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="⏱️ Downtime",
                name="Total Downtime Events",
                value=f"{downtime_events:,}",
                formula="Count(Downtime Records)",
                source=f"`{downtime_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            # Equipment availability
            operating_hours = 8 * 250  # Assume 8hr shifts, 250 working days/year
            availability = ((operating_hours - total_downtime) / operating_hours * 100) if operating_hours > 0 else 0
            
            kpis.append(safe_kpi(
                category="🔧 Equipment Health",
                name="Equipment Availability %",
                value=f"{max(0, availability):.2f}%",
                formula="(Operating Hours - Downtime) / Operating Hours * 100",
                source=f"`{downtime_col}`",
                confidence=conf,
                warnings="CRITICAL: Availability < 80%" if availability < 80 else "Low availability (80-85%)" if availability < 85 else warns
            ))
    
    # Downtime by machine
    if machine_col and pd.api.types.is_numeric_dtype(df[downtime_col]):
        machine_downtime = df.groupby(machine_col)[downtime_col].sum().sort_values(ascending=False)
        
        if not machine_downtime.empty:
            worst_machine = machine_downtime.idxmax()
            worst_downtime = machine_downtime.max()
            
            kpis.append(safe_kpi(
                category="🔧 Equipment Health",
                name="Most Problematic Machine",
                value=f"{worst_machine} ({worst_downtime:,.1f} hrs)",
                formula="Machine with max downtime",
                source=f"`{machine_col}`, `{downtime_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Downtime reason breakdown
    if reason_col:
        reason_dist = df[reason_col].value_counts().head(3)
        
        if not reason_dist.empty:
            top_reason = reason_dist.idxmax()
            
            kpis.append(safe_kpi(
                category="⏱️ Downtime",
                name="Top Downtime Reason",
                value=f"{top_reason} ({reason_dist.max()} occurrences)",
                formula="Most frequent downtime reason",
                source=f"`{reason_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
