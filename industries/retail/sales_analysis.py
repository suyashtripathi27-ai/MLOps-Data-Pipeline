"""
Retail sales, revenue trends, growth, and demand spikes.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_sales_metrics(df):
    """Calculates retail sales and revenue KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Revenue is MONEY, not time
    revenue_col = first_column(df, ["revenue", "sales", "weekly_sales", "total_sales", "order_value"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "week_date", "timestamp"])
    store_col = first_column(df, ["store_id", "store_name", "location"])
    
    if not revenue_col:
        return kpis
    
    # Revenue is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[revenue_col]):
        kpis.append(safe_kpi(
            category="💰 Sales",
            name="Sales Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{revenue_col}`",
            confidence="Low",
            warnings="Revenue column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [revenue_col, date_col, store_col] if col])
    
    # Total revenue
    valid_revenue = df[revenue_col].dropna()
    
    if not valid_revenue.empty:
        total_revenue = valid_revenue.sum()
        avg_revenue = valid_revenue.mean()
        median_revenue = valid_revenue.median()
        
        kpis.append(safe_kpi(
            category="💰 Sales",
            name="Total Revenue",
            value=f"${total_revenue:,.2f}",
            formula="Sum(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Sales",
            name="Avg Transaction Value",
            value=f"${avg_revenue:,.2f}",
            formula="Mean(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Sales",
            name="Median Transaction Value",
            value=f"${median_revenue:,.2f}",
            formula="Median(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Revenue variance
        revenue_std = valid_revenue.std()
        
        kpis.append(safe_kpi(
            category="💰 Sales",
            name="Revenue Std Dev",
            value=f"${revenue_std:,.2f}",
            formula="StdDev(Revenue)",
            source=f"`{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Date-based analysis (⏱️ EXACT DATES - validate as datetime, not duration)
    if date_col:
        date_series = pd.to_datetime(df[date_col], errors="coerce")
        dt_valid, reason = SemanticValidator.is_valid_datetime(date_series.dropna())
        
        if dt_valid and date_series.notna().sum() > 1:
            try:
                trend_df = pd.DataFrame({
                    "date": date_series,
                    "revenue": df[revenue_col]
                }).dropna()
                
                # Weekly aggregation
                weekly = trend_df.set_index("date")["revenue"].resample("W").sum().dropna()
                
                if not weekly.empty:
                    first_week = weekly.iloc[0]
                    last_week = weekly.iloc[-1]
                    growth = ((last_week - first_week) / first_week * 100) if first_week != 0 else 0
                    
                    kpis.append(safe_kpi(
                        category="📈 Sales Trends",
                        name="Revenue Growth %",
                        value=f"{growth:.2f}%",
                        formula="((Last Week - First Week) / First Week) * 100",
                        source=f"`{revenue_col}`, `{date_col}`",
                        confidence=conf,
                        warnings=warns
                    ))
                    
                    # Top period
                    top_period = weekly.idxmax()
                    top_revenue = weekly.max()
                    
                    kpis.append(safe_kpi(
                        category="📈 Sales Trends",
                        name="Peak Sales Period",
                        value=f"{top_period.strftime('%Y-%m-%d')} (${top_revenue:,.2f})",
                        formula="Period with max weekly revenue",
                        source=f"`{revenue_col}`, `{date_col}`",
                        confidence=conf,
                        warnings=warns
                    ))
                    
                    # Moving average
                    moving_avg = weekly.rolling(window=4, min_periods=1).mean().iloc[-1]
                    
                    kpis.append(safe_kpi(
                        category="📈 Sales Trends",
                        name="4-Week Moving Average",
                        value=f"${moving_avg:,.2f}",
                        formula="RollingMean(Weekly Revenue, 4 weeks)",
                        source=f"`{revenue_col}`, `{date_col}`",
                        confidence=conf,
                        warnings=warns
                    ))
                    
                    # Demand spikes
                    spike_threshold = weekly.mean() + (2 * weekly.std())
                    demand_spikes = (weekly > spike_threshold).sum() if pd.notnull(spike_threshold) else 0
                    
                    kpis.append(safe_kpi(
                        category="📈 Sales Trends",
                        name="Demand Spikes Detected",
                        value=f"{demand_spikes:,}",
                        formula="Count(Weekly Revenue > Mean + 2*StdDev)",
                        source=f"`{revenue_col}`, `{date_col}`",
                        confidence=conf,
                        warnings=warns
                    ))
            except Exception:
                pass
        else:
            kpis.append(safe_kpi(
                category="📈 Sales Trends",
                name="Trend Metrics",
                value="EXCLUDED",
                formula="N/A",
                source=f"`{date_col}`",
                confidence="Low",
                warnings=f"Invalid dates: {reason}"
            ))
    
    return kpis
