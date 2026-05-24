"""
Quality metrics, defect rates, scrap, and yield analysis.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_quality_metrics(df):
    """Calculates quality and yield KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Units are COUNT (quantity), not time
    good_col = first_column(df, ["good_units", "acceptable_units", "passed_units", "saleable_units", "first_pass"])
    scrap_col = first_column(df, ["scrap_units", "rejected_units", "defective_units", "waste_units", "rework_units"])
    total_col = first_column(df, ["total_units", "produced_units", "total_output"])
    defect_rate_col = first_column(df, ["defect_rate", "scrap_rate", "reject_rate", "defect_pct"])
    
    if not good_col and not scrap_col and not defect_rate_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [good_col, scrap_col, total_col, defect_rate_col] if col])
    
    # Saleable output
    if good_col and pd.api.types.is_numeric_dtype(df[good_col]):
        total_good = df[good_col].sum()
        
        kpis.append(safe_kpi(
            category="🔬 Quality",
            name="Total Good Units",
            value=f"{total_good:,.0f}",
            formula="Sum(Good Units)",
            source=f"`{good_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Scrap/Reject analysis
    if scrap_col and pd.api.types.is_numeric_dtype(df[scrap_col]):
        total_scrap = df[scrap_col].sum()
        
        kpis.append(safe_kpi(
            category="🔬 Quality",
            name="Total Scrap / Rejected Units",
            value=f"{total_scrap:,.0f}",
            formula="Sum(Scrap Units)",
            source=f"`{scrap_col}`",
            confidence=conf,
            warnings="High scrap - Quality issues" if total_scrap > 1000 else warns
        ))
    
    # Yield calculation
    if good_col and total_col and pd.api.types.is_numeric_dtype(df[good_col]) and pd.api.types.is_numeric_dtype(df[total_col]):
        total_good = df[good_col].sum()
        total_produced = df[total_col].sum()
        
        if total_produced > 0:
            yield_pct = (total_good / total_produced) * 100
            
            kpis.append(safe_kpi(
                category="🔬 Quality",
                name="Production Yield %",
                value=f"{yield_pct:.2f}%",
                formula="(Good Units / Total Produced) * 100",
                source=f"`{good_col}`, `{total_col}`",
                confidence=conf,
                warnings="Low yield - Quality issues" if yield_pct < 95 else warns
            ))
    
    # Defect rate
    if defect_rate_col and pd.api.types.is_numeric_dtype(df[defect_rate_col]):
        valid_defect = df[defect_rate_col].dropna()
        
        if not valid_defect.empty:
            avg_defect = valid_defect.mean()
            max_defect = valid_defect.max()
            
            kpis.append(safe_kpi(
                category="🔬 Quality",
                name="Avg Defect Rate",
                value=f"{avg_defect:.2f}%",
                formula="Mean(Defect Rate)",
                source=f"`{defect_rate_col}`",
                confidence=conf,
                warnings="High defect rate" if avg_defect > 5 else warns
            ))
            
            kpis.append(safe_kpi(
                category="🔬 Quality",
                name="Max Defect Rate",
                value=f"{max_defect:.2f}%",
                formula="Max(Defect Rate)",
                source=f"`{defect_rate_col}`",
                confidence=conf,
                warnings="Critical defect rate" if max_defect > 10 else warns
            ))
    
    # Scrap rate
    if scrap_col and total_col and pd.api.types.is_numeric_dtype(df[scrap_col]) and pd.api.types.is_numeric_dtype(df[total_col]):
        total_scrap = df[scrap_col].sum()
        total_produced = df[total_col].sum()
        
        if total_produced > 0:
            scrap_rate = (total_scrap / total_produced) * 100
            
            kpis.append(safe_kpi(
                category="🔬 Quality",
                name="Scrap Rate %",
                value=f"{scrap_rate:.2f}%",
                formula="(Total Scrap / Total Produced) * 100",
                source=f"`{scrap_col}`, `{total_col}`",
                confidence=conf,
                warnings="High scrap rate" if scrap_rate > 5 else warns
            ))
    
    return kpis
