import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, excluded_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_sales_metrics(df):
    kpis = []
    if len(df) == 0:
        return kpis
        
    revenue_col = first_column(df, ["revenue", "sales", "order_value", "total_sales", "gmv"])
    date_col = first_column(df, ["date", "transaction_date", "order_date", "timestamp"])
    
    if not revenue_col:
        return kpis

    # 🛑 FIX: Used numeric validation for money, NOT duration!
    if not pd.api.types.is_numeric_dtype(df[revenue_col]):
        kpis.append(excluded_kpi(
            "🛒 Sales Analysis", 
            "Sales Metrics", 
            f"`{revenue_col}`", 
            "Revenue column contains non-numeric data."
        ))
        return kpis

    valid_revenue = df[revenue_col].dropna()
    if valid_revenue.empty:
        return kpis

    conf, warns = confidence_for(df, [revenue_col, date_col] if date_col else [revenue_col])
    
    kpis.append(safe_kpi("🛒 Sales Analysis", "Total Revenue", f"${valid_revenue.sum():,.2f}", "Sum(revenue)", f"`{revenue_col}`", conf, warns))
    kpis.append(safe_kpi("🛒 Sales Analysis", "Avg Order Value", f"${valid_revenue.mean():,.2f}", "Mean(order value)", f"`{revenue_col}`", conf, warns))
    kpis.append(safe_kpi("🛒 Sales Analysis", "Median Order Value", f"${valid_revenue.median():,.2f}", "Median(order value)", f"`{revenue_col}`", conf, warns))
    kpis.append(safe_kpi("🛒 Sales Analysis", "Revenue Variance", f"{valid_revenue.var():,.2f}", "Var(order value)", f"`{revenue_col}`", conf, warns))

    if date_col:
        dt_series = pd.to_datetime(df[date_col], errors="coerce")
        dt_valid, dt_reason = SemanticValidator.is_valid_datetime(dt_series.dropna())
        
        if dt_valid and dt_series.notna().sum() > 1:
            trend_df = pd.DataFrame({"date": dt_series, "revenue": df[revenue_col]}).dropna()
            
            # Note: Changed 'M' to 'ME' (Month End) to avoid Pandas warnings
            monthly = trend_df.set_index("date")["revenue"].resample("ME").sum().dropna()
            
            if not monthly.empty:
                first_period = monthly.iloc[0]
                last_period = monthly.iloc[-1]
                growth = ((last_period - first_period) / first_period) * 100 if first_period != 0 else 0
                peak_period = monthly.idxmax().strftime("%Y-%m-%d")
                rolling_avg = monthly.rolling(window=3, min_periods=1).mean().iloc[-1]
                
                kpis.append(safe_kpi("🛒 Sales Analysis", "Revenue Growth %", f"{growth:.2f}%", "((Last - First) / First) * 100", f"`{revenue_col}`, `{date_col}`", conf, warns))
                kpis.append(safe_kpi("🛒 Sales Analysis", "Peak Revenue Period", peak_period, "ArgMax(Monthly Revenue)", f"`{revenue_col}`, `{date_col}`", conf, warns))
                kpis.append(safe_kpi("🛒 Sales Analysis", "3-Period Moving Average", f"${rolling_avg:,.2f}", "RollingMean(Monthly Revenue, 3)", f"`{revenue_col}`, `{date_col}`", conf, warns))
        else:
            kpis.append(excluded_kpi("🛒 Sales Analysis", "Trend Metrics", f"`{date_col}`", dt_reason))

    return kpis
