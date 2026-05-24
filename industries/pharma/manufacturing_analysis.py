"""
Pharmaceutical manufacturing, batch yield, OOS rate, and quality metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_manufacturing_metrics(df):
    """Calculates pharma manufacturing and quality KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Yield and OOS are percentages/ratios, not time
    yield_col = first_column(df, ["batch_yield", "yield_percentage", "production_yield", "yield_pct"])
    oos_col = first_column(df, ["oos_rate", "out_of_spec_rate", "oos_count", "out_of_specification"])
    batch_col = first_column(df, ["batch_id", "batch_number", "lot_number"])
    product_col = first_column(df, ["product_id", "drug_product", "formulation"])
    
    if not yield_col and not oos_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [yield_col, oos_col, batch_col, product_col] if col])
    
    # Batch yield
    if yield_col and pd.api.types.is_numeric_dtype(df[yield_col]):
        valid_yield = df[yield_col].dropna()
        
        if not valid_yield.empty:
            avg_yield = valid_yield.mean()
            min_yield = valid_yield.min()
            
            kpis.append(safe_kpi(
                category="🏭 Manufacturing",
                name="Avg Batch Yield",
                value=f"{avg_yield:.2f}%",
                formula="Mean(Batch Yield %)",
                source=f"`{yield_col}`",
                confidence=conf,
                warnings="Suboptimal production yield (<90%)" if avg_yield < 90 else "Low yield (90-95%)" if avg_yield < 95 else warns
            ))
            
            kpis.append(safe_kpi(
                category="🏭 Manufacturing",
                name="Min Batch Yield",
                value=f"{min_yield:.2f}%",
                formula="Min(Batch Yield %)",
                source=f"`{yield_col}`",
                confidence=conf,
                warnings="CRITICAL: Extremely low batch yield" if min_yield < 80 else warns
            ))
    
    # Out of Specification (OOS) rate
    if oos_col and pd.api.types.is_numeric_dtype(df[oos_col]):
        valid_oos = df[oos_col].dropna()
        
        if not valid_oos.empty:
            avg_oos = valid_oos.mean()
            max_oos = valid_oos.max()
            
            kpis.append(safe_kpi(
                category="🏭 Manufacturing",
                name="Avg Out-of-Spec (OOS) Rate",
                value=f"{avg_oos:.2f}%",
                formula="Mean(OOS Rate %)",
                source=f"`{oos_col}`",
                confidence=conf,
                warnings="Critical OOS levels (>5%)" if avg_oos > 5 else "High OOS (2-5%)" if avg_oos > 2 else warns
            ))
            
            kpis.append(safe_kpi(
                category="🏭 Manufacturing",
                name="Max OOS Rate (Worst Batch)",
                value=f"{max_oos:.2f}%",
                formula="Max(OOS Rate %)",
                source=f"`{oos_col}`",
                confidence=conf,
                warnings="Unacceptable OOS level" if max_oos > 10 else warns
            ))
    
    # Total batches
    if batch_col:
        total_batches = df[batch_col].nunique()
        
        kpis.append(safe_kpi(
            category="🏭 Manufacturing",
            name="Total Batches",
            value=f"{total_batches:,}",
            formula="Count(Distinct Batches)",
            source=f"`{batch_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Product-wise performance
    if product_col and yield_col and pd.api.types.is_numeric_dtype(df[yield_col]):
        product_yield = df.groupby(product_col)[yield_col].mean().sort_values()
        
        if not product_yield.empty:
            worst_product = product_yield.idxmin()
            worst_yield = product_yield.min()
            
            kpis.append(safe_kpi(
                category="🏭 Manufacturing",
                name="Lowest Yielding Product",
                value=f"{worst_product} ({worst_yield:.2f}%)",
                formula="Product with min avg yield",
                source=f"`{product_col}`, `{yield_col}`",
                confidence=conf,
                warnings="Critical: Investigate formulation" if worst_yield < 85 else warns
            ))
    
    return kpis
