"""
Demand forecasting and forecast accuracy KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_forecasting_metrics(df, enable_debug=False):
    """
    Calculates demand and forecast accuracy KPIs with optional execution tracing.
    
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
    
    forecast_col, forecast_series = engine.get_numeric(["forecast_units", "forecast_volume", "predicted_demand"])
    actual_col, actual_series = engine.get_numeric(["actual_units", "actual_demand", "realized_demand"])
    
    # ==========================================
    # 1. FORECASTED VOLUME
    # ==========================================
    if forecast_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        forecast_clean = forecast_series.dropna()
        
        if len(forecast_clean) > 0:
            total_forecast = forecast_clean.sum()
            avg_forecast = forecast_clean.mean()
            
            kpis.append(engine.build_kpi(
                category="📈 Forecasting",
                name="Forecasted Volume",
                value=f"{total_forecast:,.0f} units",
                formula="Sum(Forecast)",
                source=f"`{forecast_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="📈 Forecasting",
                name="Avg Forecasted Units",
                value=f"{avg_forecast:,.0f} units",
                formula="Mean(Forecast)",
                source=f"`{forecast_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📈 Forecasting", "Forecast Volume", "All forecast entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📈 Forecasting", "Forecast Volume", "Missing numeric 'forecast_units' column."))
    
    # ==========================================
    # 2. FORECAST ACCURACY
    # ==========================================
    if forecast_col is not None and actual_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        forecast_clean = pd.concat([forecast_series, actual_series], axis=1).dropna()
        
        if len(forecast_clean) > 0:
            forecast_total = forecast_clean[forecast_col].sum()
            actual_total = forecast_clean[actual_col].sum()
            
            if actual_total > 0:
                accuracy = (1 - abs(actual_total - forecast_total) / actual_total) * 100
            else:
                accuracy = 0
            
            warn_msg = "Poor forecast accuracy (<80%)" if accuracy < 80 else "None"
            kpis.append(engine.build_kpi(
                category="📈 Forecasting",
                name="Forecast Accuracy",
                value=f"{accuracy:.2f}%",
                formula="(1 - |Actual - Forecast| / Actual) * 100",
                source=f"`{forecast_col}`, `{actual_col}`",
                warnings=warn_msg
            ))
            
            kpis.append(engine.build_kpi(
                category="📈 Forecasting",
                name="Total Actual Demand",
                value=f"{actual_total:,.0f} units",
                formula="Sum(Actual)",
                source=f"`{actual_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📈 Forecasting", "Accuracy", "Missing valid forecast/actual data."))
    else:
        kpis.append(engine.log_missing("📈 Forecasting", "Accuracy", "Missing 'actual_units' or 'forecast_units' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
