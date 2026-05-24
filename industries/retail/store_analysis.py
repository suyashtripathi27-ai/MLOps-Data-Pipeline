"""
Store performance, revenue by location, and store profitability metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_store_metrics(df):
    """Calculates store-level performance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Store metrics
    store_col = first_column(df, ["store_id", "store_name", "store", "outlet_id", "location"])
    revenue_col = first_column(df, ["revenue", "sales", "weekly_sales", "total_sales", "store_revenue"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "week_date"])
    
    if not store_col or not revenue_col:
        return kpis
    
    # Revenue is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[revenue_col]):
        kpis.append(safe_kpi(
            category="🏬 Store",
            name="Store Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{store_col}`, `{revenue_col}`",
            confidence="Low",
            warnings="Revenue column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [store_col, revenue_col, date_col] if col])
    
    # Total stores
    total_stores = df[store_col].nunique()
    
    kpis.append(safe_kpi(
        category="🏬 Store",
        name="Total Stores",
        value=f"{total_stores}",
        formula="Count(Distinct Stores)",
        source=f"`{store_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Revenue by store
    valid_df = df[[store_col, revenue_col]].dropna()
    
    if not valid_df.empty:
        store_rev = valid_df.groupby(store_col)[revenue_col].sum().sort_values(ascending=False)
        total_revenue = store_rev.sum()
        
        kpis.append(safe_kpi(
            category="🏬 Store",
            name="Total Store Revenue",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Store Revenue)",
            source=f"`{store_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="🏬 Store",
            name="Avg Revenue per Store",
            value=f"${store_rev.mean():,.2f}",
            formula="Mean(Store Revenue)",
            source=f"`{store_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Top stores
        top_store = store_rev.idxmax()
        top_store_revenue = store_rev.max()
        
        kpis.append(safe_kpi(
            category="🏬 Store",
            name="Top Performing Store",
            value=f"{top_store} (${top_store_revenue:,.2f})",
            formula="Store with max revenue",
            source=f"`{store_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Worst store
        worst_store = store_rev.idxmin()
        worst_store_revenue = store_rev.min()
        
        kpis.append(safe_kpi(
            category="🏬 Store",
            name="Lowest Performing Store",
            value=f"{worst_store} (${worst_store_revenue:,.2f})",
            formula="Store with min revenue",
            source=f"`{store_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Concentration analysis
        top_10_contrib = (store_rev.head(10).sum() / total_revenue * 100) if total_revenue > 0 else 0
        
        kpis.append(safe_kpi(
            category="🏬 Store",
            name="Top 10 Store Contribution",
            value=f"{top_10_contrib:.2f}%",
            formula="(Top 10 Revenue / Total) * 100",
            source=f"`{store_col}`, `{revenue_col}`",
            confidence=conf,
            warnings="High concentration - Risk in top stores" if top_10_contrib > 70 else warns
        ))
    
    # Store growth (⏱️ EXACT DATES - not duration)
    if date_col:
        date_series = pd.to_datetime(df[date_col], errors="coerce")
        dt_valid, _ = SemanticValidator.is_valid_datetime(date_series.dropna())
        
        if dt_valid:
            try:
                growth_df = df[[store_col, revenue_col]].copy()
                growth_df["date"] = date_series
                growth_df = growth_df.dropna(subset=["date", store_col, revenue_col])
                
                if not growth_df.empty:
                    by_store_month = growth_df.groupby([store_col, pd.Grouper(key="date", freq="M")])[revenue_col].sum()
                    
                    growth_rates = []
                    for _, series in by_store_month.groupby(level=0):
                        values = series.values
                        if len(values) >= 2 and values[0] != 0:
                            growth = ((values[-1] - values[0]) / values[0]) * 100
                            growth_rates.append(growth)
                    
                    if growth_rates:
                        avg_growth = pd.Series(growth_rates).mean()
                        
                        kpis.append(safe_kpi(
                            category="📈 Store Growth",
                            name="Avg Store Growth Rate",
                            value=f"{avg_growth:.2f}%",
                            formula="Mean(Store Growth First to Last Period)",
                            source=f"`{store_col}`, `{revenue_col}`, `{date_col}`",
                            confidence=conf,
                            warnings=warns
                        ))
            except Exception:
                pass
    
    return kpis
