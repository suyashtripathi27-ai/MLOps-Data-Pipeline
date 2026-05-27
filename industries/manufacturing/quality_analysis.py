"""
Quality metrics, defect rates, scrap, and yield analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_quality_metrics(df, enable_debug=False):
    """
    Calculates quality and yield KPIs with optional execution tracing.
    
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
    good_col, good_series = engine.get_numeric(["good_units", "acceptable_units", "passed_units", "saleable_units", "first_pass"])
    scrap_col, scrap_series = engine.get_numeric(["scrap_units", "rejected_units", "defective_units", "waste_units", "rework_units"])
    total_col, total_series = engine.get_numeric(["total_units", "produced_units", "total_output"])
    defect_rate_col, defect_rate_series = engine.get_numeric(["defect_rate", "scrap_rate", "reject_rate", "defect_pct"])
    
    # ==========================================
    # 1. SALEABLE OUTPUT
    # ==========================================
    if good_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        good_clean = good_series.dropna()
        
        if len(good_clean) > 0:
            total_good = good_clean.sum()
            
            kpis.append(engine.build_kpi(
                category="🔬 Quality",
                name="Total Good Units",
                value=f"{total_good:,.0f}",
                formula="Sum(Good Units)",
                source=f"`{good_col}`"
            ))
        else:
            kpis.append(engine.log_missing("🔬 Quality", "Good Units", "All good units entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🔬 Quality", "Good Units", "Missing 'good_units' column."))
    
    # ==========================================
    # 2. SCRAP/REJECT ANALYSIS
    # ==========================================
    if scrap_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        scrap_clean = scrap_series.dropna()
        
        if len(scrap_clean) > 0:
            total_scrap = scrap_clean.sum()
            
            warn_msg = "High scrap - Quality issues" if total_scrap > 1000 else "None"
            kpis.append(engine.build_kpi(
                category="🔬 Quality",
                name="Total Scrap / Rejected Units",
                value=f"{total_scrap:,.0f}",
                formula="Sum(Scrap Units)",
                source=f"`{scrap_col}`",
                warnings=warn_msg
            ))
        else:
            kpis.append(engine.log_missing("🔬 Quality", "Scrap Units", "All scrap units entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🔬 Quality", "Scrap Units", "Missing 'scrap_units' column."))
    
    # ==========================================
    # 3. YIELD CALCULATION
    # ==========================================
    if good_col is not None and total_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        yield_clean = pd.concat([good_series, total_series], axis=1).dropna()
        
        if len(yield_clean) > 0:
            total_good = yield_clean[good_col].sum()
            total_produced = yield_clean[total_col].sum()
            
            if total_produced > 0:
                yield_pct = (total_good / total_produced) * 100
                
                warn_msg = "Low yield - Quality issues (<95%)" if yield_pct < 95 else "None"
                kpis.append(engine.build_kpi(
                    category="🔬 Quality",
                    name="Production Yield %",
                    value=f"{yield_pct:.2f}%",
                    formula="(Good Units / Total Produced) * 100",
                    source=f"`{good_col}`, `{total_col}`",
                    warnings=warn_msg
                ))
        else:
            kpis.append(engine.log_missing("🔬 Quality", "Yield", "Missing valid good_units/total_units data."))
    else:
        kpis.append(engine.log_missing("🔬 Quality", "Yield", "Missing 'good_units' or 'total_units' column."))
    
    # ==========================================
    # 4. DEFECT RATE
    # ==========================================
    if defect_rate_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        defect_clean = defect_rate_series.dropna()
        
        if len(defect_clean) > 0:
            avg_defect = defect_clean.mean()
            max_defect = defect_clean.max()
            
            kpis.append(engine.build_kpi(
                category="🔬 Quality",
                name="Avg Defect Rate",
                value=f"{avg_defect:.2f}%",
                formula="Mean(Defect Rate)",
                source=f"`{defect_rate_col}`",
                warnings="High defect rate (>5%)" if avg_defect > 5 else "None"
            ))
            
            kpis.append(engine.build_kpi(
                category="🔬 Quality",
                name="Max Defect Rate",
                value=f"{max_defect:.2f}%",
                formula="Max(Defect Rate)",
                source=f"`{defect_rate_col}`",
                warnings="Critical defect rate (>10%)" if max_defect > 10 else "None"
            ))
        else:
            kpis.append(engine.log_missing("🔬 Quality", "Defect Rate", "All defect rate entries are missing/null."))
    else:
        kpis.append(engine.log_missing("🔬 Quality", "Defect Rate", "Missing 'defect_rate' column."))
    
    # ==========================================
    # 5. SCRAP RATE
    # ==========================================
    if scrap_col is not None and total_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        scrap_rate_clean = pd.concat([scrap_series, total_series], axis=1).dropna()
        
        if len(scrap_rate_clean) > 0:
            total_scrap = scrap_rate_clean[scrap_col].sum()
            total_produced = scrap_rate_clean[total_col].sum()
            
            if total_produced > 0:
                scrap_rate = (total_scrap / total_produced) * 100
                
                warn_msg = "High scrap rate (>5%)" if scrap_rate > 5 else "None"
                kpis.append(engine.build_kpi(
                    category="🔬 Quality",
                    name="Scrap Rate %",
                    value=f"{scrap_rate:.2f}%",
                    formula="(Total Scrap / Total Produced) * 100",
                    source=f"`{scrap_col}`, `{total_col}`",
                    warnings=warn_msg
                ))
        else:
            kpis.append(engine.log_missing("🔬 Quality", "Scrap Rate", "Missing valid scrap_units/total_units data."))
    else:
        kpis.append(engine.log_missing("🔬 Quality", "Scrap Rate", "Missing 'scrap_units' or 'total_units' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
