"""
Hub congestion, performance, and cutoff analysis.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_hub_intelligence(df):
    """Calculates hub performance and congestion KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    hub_col = first_column(df, ["source_name", "hub_name", "facility_name", "hub_id"])
    actual_time_col = first_column(df, ["actual_time", "actual_timestamp", "arrival_time"])
    planned_time_col = first_column(df, ["planned_time", "osrm_time", "estimated_time"])
    cutoff_col = first_column(df, ["is_cutoff", "cutoff_flag", "missed_cutoff"])
    throughput_col = first_column(df, ["throughput", "items_processed", "packages_processed"])
    
    if not hub_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [hub_col, actual_time_col, planned_time_col, cutoff_col, throughput_col] if col])
    
    # Total hubs
    total_hubs = df[hub_col].nunique()
    
    kpis.append(safe_kpi(
        category="🏢 Hub Network",
        name="Total Distribution Hubs",
        value=f"{total_hubs}",
        formula="Count(Distinct Hubs)",
        source=f"`{hub_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Hub delays (⏱️ TIME-BASED - Validate with SemanticValidator)
    if actual_time_col and planned_time_col:
        # Check if datetime
        actual_dt = pd.to_datetime(df[actual_time_col], errors="coerce")
        planned_dt = pd.to_datetime(df[planned_time_col], errors="coerce")
        
        # Validate as datetime
        actual_valid, actual_reason = SemanticValidator.is_valid_datetime(actual_dt.dropna())
        planned_valid, planned_reason = SemanticValidator.is_valid_datetime(planned_dt.dropna())
        
        if actual_valid and planned_valid:
            delay_df = pd.DataFrame({
                "hub": df[hub_col],
                "delay": (actual_dt - planned_dt).dt.total_seconds() / 60  # Convert to minutes
            }).dropna()
            
            if not delay_df.empty:
                valid_delays = delay_df[delay_df["delay"] > 0.1]
                
                if not valid_delays.empty:
                    worst_hub = valid_delays.groupby("hub")["delay"].mean().idxmax()
                    worst_delay = valid_delays.groupby("hub")["delay"].mean().max()
                    avg_delay = valid_delays["delay"].mean()
                    
                    kpis.append(safe_kpi(
                        category="🏢 Hub Congestion",
                        name="Most Congested Hub",
                        value=f"{worst_hub} ({worst_delay:.1f} min avg delay)",
                        formula="Hub with max avg delay",
                        source=f"`{hub_col}`, `{actual_time_col}`, `{planned_time_col}`",
                        confidence=conf,
                        warnings=warns
                    ))
                    
                    kpis.append(safe_kpi(
                        category="🏢 Hub Congestion",
                        name="Network Avg Delay",
                        value=f"{avg_delay:.1f} mins",
                        formula="Mean(Actual - Planned) > 0",
                        source=f"`{actual_time_col}`, `{planned_time_col}`",
                        confidence=conf,
                        warnings="High delays - Capacity issues" if avg_delay > 60 else warns
                    ))
        else:
            kpis.append(safe_kpi(
                category="🏢 Hub Congestion",
                name="Hub Delay Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{actual_time_col}`, `{planned_time_col}`",
                confidence="Low",
                warnings=f"Invalid timestamp: Actual={actual_reason}, Planned={planned_reason}"
            ))
    
    # Cutoff performance
    if cutoff_col:
        cutoff_mask = df[cutoff_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'missed'])
        cutoff_count = cutoff_mask.sum()
        cutoff_rate = (cutoff_count / len(df) * 100) if len(df) > 0 else 0
        
        kpis.append(safe_kpi(
            category="🏢 Hub Performance",
            name="Missed Cutoff Rate",
            value=f"{cutoff_rate:.2f}%",
            formula="(Missed Cutoffs / Total) * 100",
            source=f"`{cutoff_col}`",
            confidence=conf,
            warnings="Critical SLA failure" if cutoff_rate > 10 else warns
        ))
        
        # Worst hub for cutoffs
        if hub_col and cutoff_col:
            worst_cutoff_hub = df[cutoff_mask].groupby(hub_col).size().idxmax() if cutoff_count > 0 else None
            
            if worst_cutoff_hub:
                worst_cutoff_count = df[cutoff_mask].groupby(hub_col).size().max()
                
                kpis.append(safe_kpi(
                    category="🏢 Hub Performance",
                    name="Highest Cutoff Concentration",
                    value=f"{worst_cutoff_hub} ({worst_cutoff_count} failures)",
                    formula="Hub with most missed cutoffs",
                    source=f"`{hub_col}`, `{cutoff_col}`",
                    confidence=conf,
                    warnings=warns
                ))
    
    # Throughput analysis
    if throughput_col and pd.api.types.is_numeric_dtype(df[throughput_col]):
        total_throughput = df[throughput_col].sum()
        avg_throughput = df[throughput_col].mean()
        
        kpis.append(safe_kpi(
            category="🏢 Hub Capacity",
            name="Total Network Throughput",
            value=f"{total_throughput:,.0f} items",
            formula="Sum(Throughput)",
            source=f"`{throughput_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🏢 Hub Capacity",
            name="Avg Hub Throughput",
            value=f"{avg_throughput:,.0f} items",
            formula="Mean(Throughput)",
            source=f"`{throughput_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
