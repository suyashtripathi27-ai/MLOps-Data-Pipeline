"""
Financial forecasting, projections, and variance analysis.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_forecasting_metrics(df, enable_debug=False):
    """
    Calculate forecasting and variance KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    
    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    forecast_col, forecast_series = engine.get_numeric(["forecast", "projected", "budget", "estimate"])
    actual_col, actual_series = engine.get_numeric(["actual", "realized", "actuals", "true_value"])
    
    if forecast_col is None or actual_col is None:
        kpis.append(engine.log_missing("🔮 Forecasting", "Forecast vs Actual", "Missing 'forecast' or 'actual'."))
        return kpis
    
    # Forecast accuracy
    df_temp = pd.concat([forecast_series, actual_series], axis=1).dropna()
    
    if len(df_temp) > 0:
        variance = df_temp[actual_col] - df_temp[forecast_col]
        pct_variance = (variance / (df_temp[actual_col] + 0.0001)) * 100
        
        avg_variance = variance.mean()
        avg_pct_variance = pct_variance.mean()
        abs_pct_variance = pct_variance.abs().mean()
        
        kpis.append(engine.build_kpi(
            category="🔮 Forecasting", name="Avg Forecast Variance $",
            value=f"${avg_variance:,.2f}", formula="Mean(Actual - Forecast)", 
            source=f"`{actual_col}`, `{forecast_col}`"
        ))
        
        warn_msg = "High forecast error (>10%)" if abs_pct_variance > 10 else "Moderate error (>5%)" if abs_pct_variance > 5 else "None"
        kpis.append(engine.build_kpi(
            category="🔮 Forecasting", name="Forecast Accuracy %",
            value=f"{100 - abs_pct_variance:.2f}%", formula="100 - Mean(|Actual-Forecast|/Actual*100)", 
            source=f"`{actual_col}`, `{forecast_col}`",
            warnings=warn_msg
        ))
        
        # High and low variance items
        high_variance_items = (pct_variance.abs() > pct_variance.abs().quantile(0.75)).sum()
        high_variance_pct = (high_variance_items / len(df_temp) * 100) if len(df_temp) > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="🔮 Forecasting", name="High Variance Items (Top 25%)",
            value=f"{high_variance_pct:.2f}%", formula="(|Variance| > 75th Percentile) / Total * 100", 
            source=f"`{actual_col}`, `{forecast_col}`"
        ))
        
        # Total budget vs actual
        total_forecast = forecast_series.sum()
        total_actual = actual_series.sum()
        total_variance_pct = ((total_actual - total_forecast) / total_forecast * 100) if total_forecast > 0 else 0
        
        warn_msg = "Budget overrun (>5%)" if total_variance_pct > 5 else "Budget underrun (>5%)" if total_variance_pct < -5 else "None"
        kpis.append(engine.build_kpi(
            category="🔮 Forecasting", name="Total Budget Variance %",
            value=f"{total_variance_pct:.2f}%", formula="((Total Actual - Total Forecast) / Forecast) * 100", 
            source=f"`{actual_col}`, `{forecast_col}`",
            warnings=warn_msg
        ))

    if enable_debug:
        engine.print_execution_log()
    
    return kpis
