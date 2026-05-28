"""
Hub congestion, performance, and cutoff analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

LOGISTICS_CONFIG = {
    "missing_data_threshold": 5,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_hub_intelligence(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=LOGISTICS_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    hub_col, hub_series = engine.get_column(["source_name", "hub_name", "facility_name", "hub_id"])
    actual_col, actual_series = engine.get_datetime(["actual_time", "actual_timestamp", "arrival_time"])
    planned_col, planned_series = engine.get_datetime(["planned_time", "osrm_time", "estimated_time"])
    cutoff_col, cutoff_series = engine.get_column(["is_cutoff", "cutoff_flag", "missed_cutoff"])
    throughput_col, throughput_series = engine.get_numeric(["throughput", "items_processed", "packages_processed"])
    
    if hub_col is not None:
        kpis.append(engine.build_kpi(
            category="🏢 Hub Network", name="Total Distribution Hubs",
            value=f"{hub_series.nunique()}", formula="Count(Distinct Hubs)", source=f"`{hub_col}`"
        ))
    else:
        kpis.append(engine.log_missing("🏢 Hub Network", "Hub Count", "Missing 'hub_id' column."))

    # Hub Delays
    if actual_col is not None and planned_col is not None and hub_col is not None:
        delay_df = pd.concat([hub_series, actual_series, planned_series], axis=1).dropna()
        if len(delay_df) > 0:
            delay_df["delay_mins"] = (delay_df[actual_col] - delay_df[planned_col]).dt.total_seconds() / 60
            valid_delays = delay_df[delay_df["delay_mins"] > 0]
            
            if not valid_delays.empty:
                avg_delay = valid_delays["delay_mins"].mean()
                worst_hub = valid_delays.groupby(hub_col)["delay_mins"].mean().idxmax()
                worst_delay = valid_delays.groupby(hub_col)["delay_mins"].mean().max()
                
                kpis.append(engine.build_kpi(
                    category="🏢 Hub Congestion", name="Network Avg Delay",
                    value=f"{avg_delay:.1f} mins", formula="Mean(Actual - Planned) > 0", 
                    source=f"`{actual_col}`, `{planned_col}`", warnings="High delays" if avg_delay > 60 else "None"
                ))
                kpis.append(engine.build_kpi(
                    category="🏢 Hub Congestion", name="Most Congested Hub",
                    value=f"{worst_hub} ({worst_delay:.1f} min avg)", formula="Hub with max avg delay", 
                    source=f"`{hub_col}`, `{actual_col}`"
                ))
        else:
            kpis.append(engine.log_missing("🏢 Hub Congestion", "Hub Delays", "Missing valid overlapping timestamps."))
    else:
        kpis.append(engine.log_missing("🏢 Hub Congestion", "Hub Delays", "Requires 'actual_time', 'planned_time', and 'hub'."))

    # Cutoffs
    if cutoff_col is not None:
        cutoff_clean = cutoff_series.dropna().astype(str).str.lower()
        if len(cutoff_clean) > 0:
            missed_cutoffs = cutoff_clean.isin(['1', 'true', 'yes', 'missed']).sum()
            cutoff_rate = (missed_cutoffs / len(cutoff_clean)) * 100
            
            kpis.append(engine.build_kpi(
                category="🏢 Hub Performance", name="Missed Cutoff Rate",
                value=f"{cutoff_rate:.2f}%", formula="(Missed Cutoffs / Valid Rows) * 100", 
                source=f"`{cutoff_col}`", warnings="Critical SLA failure" if cutoff_rate > 10 else "None"
            ))
    
    # Throughput
    if throughput_col is not None:
        tp_clean = throughput_series.dropna()
        if len(tp_clean) > 0:
            kpis.append(engine.build_kpi(
                category="🏢 Hub Capacity", name="Total Network Throughput",
                value=f"{tp_clean.sum():,.0f} items", formula="Sum(Throughput)", source=f"`{throughput_col}`"
            ))

    if enable_debug: engine.print_execution_log()
    return kpis
