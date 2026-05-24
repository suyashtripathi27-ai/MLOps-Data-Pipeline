"""
Seasonal patterns, holiday uplift, and demand variability metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_seasonality_metrics(df):
    """Calculates seasonality and temporal patterns KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Revenue is MONEY, not time
    revenue_col = first_column(df, ["revenue", "sales", "weekly_sales", "total_sales", "order_value"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "week_date", "timestamp"])
    holiday_col = first_column(df, ["is_holiday", "holiday_flag", "holiday"])
    
    if not revenue_col or not date_col:
        return kpis
    
    # Revenue is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[revenue_col]):
        kpis.append(safe_kpi(
            category="📅 Seasonality",
            name="Seasonality Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{revenue_col}`, `{date_col}`",
            confidence="Low",
            warnings="Revenue column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [revenue_col, date_col, holiday_col] if col])
    
    # Date validation (⏱️ EXACT DATES - not duration)
    date_series = pd.to_datetime(df[date_col], errors="coerce")
    dt_valid, reason = SemanticValidator.is_valid_datetime(date_series.dropna())
    
    if not dt_valid:
        kpis.append(safe_kpi(
            category="📅 Seasonality",
            name="Seasonality Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{date_col}`",
            confidence="Low",
            warnings=f"Invalid dates: {reason}"
        ))
        return kpis
    
    work_df = df[[revenue_col]].copy()
    work_df["date"] = date_series
    work_df = work_df.dropna(subset=["date", revenue_col])
    
    if work_df.empty:
        return kpis
    
    # Monthly and quarterly analysis
    work_df["month"] = work_df["date"].dt.month
    work_df["quarter"] = work_df["date"].dt.quarter
    
    monthly = work_df.groupby("month")[revenue_col].sum()
    
    if not monthly.empty:
        peak_month = int(monthly.idxmax())
        peak_revenue = monthly.max()
        
        kpis.append(safe_kpi(
            category="📅 Seasonality",
            name="Peak Sales Month",
            value=f"Month {peak_month} (${peak_revenue:,.2f})",
            formula="Month with max revenue",
            source=f"`{revenue_col}`, `{date_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Q4 analysis
    total_revenue = work_df[revenue_col].sum()
    q4_revenue = work_df.loc[work_df["quarter"] == 4, revenue_col].sum()
    q4_share = (q4_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    kpis.append(safe_kpi(
        category="📅 Seasonality",
        name="Q4 Contribution",
        value=f"{q4_share:.2f}%",
        formula="Q4 Revenue / Total Revenue * 100",
        source=f"`{revenue_col}`, `{date_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Demand variability
    demand_variability = work_df[revenue_col].std() / work_df[revenue_col].mean() if work_df[revenue_col].mean() > 0 else 0
    
    kpis.append(safe_kpi(
        category="📅 Seasonality",
        name="Demand Variability Coefficient",
        value=f"{demand_variability:.3f}",
        formula="StdDev(Revenue) / Mean(Revenue)",
        source=f"`{revenue_col}`",
        confidence=conf,
        warnings="High variability - Complex forecasting" if demand_variability > 0.5 else warns
    ))
    
    # Seasonal growth
    monthly_ordered = work_df.set_index("date")[revenue_col].resample("M").sum()
    
    if len(monthly_ordered) >= 2 and monthly_ordered.iloc[0] != 0:
        seasonal_growth = ((monthly_ordered.iloc[-1] - monthly_ordered.iloc[0]) / monthly_ordered.iloc[0]) * 100
        
        kpis.append(safe_kpi(
            category="📅 Seasonality",
            name="Seasonal Growth %",
            value=f"{seasonal_growth:.2f}%",
            formula="((Last Month - First Month) / First Month) * 100",
            source=f"`{revenue_col}`, `{date_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Holiday uplift
    if holiday_col:
        holiday_mask = df[holiday_col].astype(str).str.lower().isin(['true', '1', 'yes', 'y'])
        holiday_df = pd.DataFrame({
            "is_holiday": holiday_mask,
            "revenue": df[revenue_col]
        }).dropna()
        
        if holiday_df["is_holiday"].any() and (~holiday_df["is_holiday"]).any():
            holiday_avg = holiday_df.loc[holiday_df["is_holiday"], "revenue"].mean()
            non_holiday_avg = holiday_df.loc[~holiday_df["is_holiday"], "revenue"].mean()
            
            uplift = ((holiday_avg - non_holiday_avg) / non_holiday_avg * 100) if non_holiday_avg > 0 else 0
            
            kpis.append(safe_kpi(
                category="📅 Seasonality",
                name="Holiday Sales Uplift",
                value=f"{uplift:.2f}%",
                formula="((Holiday Avg - Non-Holiday Avg) / Non-Holiday Avg) * 100",
                source=f"`{holiday_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
