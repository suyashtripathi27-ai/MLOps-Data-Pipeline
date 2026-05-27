"""
Demand planning, forecast accuracy, and demand patterns.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

MANUFACTURING_CONFIG = {
    "missing_data_threshold": 6,
    "score_deduction_for_warning": 15,
    "low_confidence_threshold": 30,
}

def calc_demand_metrics(df, enable_debug=False):
    """
    Calculates demand planning KPIs with optional execution tracing.
    
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
    
    # Demand is COUNT (quantity), not time
    actual_demand_col, actual_demand_series = engine.get_numeric(["actual_demand", "orders_received", "sales_volume"])
    forecast_col, forecast_series = engine.get_numeric(["forecasted_demand", "predicted_demand", "planned_demand"])
    date_col, date_series = engine.get_datetime(["date", "period", "month"])
    product_col, product_series = engine.get_column(["product_id", "product", "sku"])
    
    # ==========================================
    # 1. DEMAND VOLUME
    # ==========================================
    if actual_demand_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        demand_clean = actual_demand_series.dropna()
        
        if len(demand_clean) > 0:
            total_demand = demand_clean.sum()
            avg_demand = demand_clean.mean()
            
            kpis.append(engine.build_kpi(
                category="📊 Demand",
                name="Total Actual Demand",
                value=f"{total_demand:,.0f} units",
                formula="Sum(Actual Demand)",
                source=f"`{actual_demand_col}`"
            ))
            
            kpis.append(engine.build_kpi(
                category="📊 Demand",
                name="Avg Demand per Period",
                value=f"{avg_demand:,.0f} units",
                formula="Mean(Actual Demand)",
                source=f"`{actual_demand_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📊 Demand", "Demand Volume", "All demand entries are missing/null."))
    else:
        kpis.append(engine.log_missing("📊 Demand", "Demand Volume", "Missing numeric 'actual_demand'."))
    
    # ==========================================
    # 2. FORECAST ACCURACY
    # ==========================================
    if actual_demand_col is not None and forecast_col is not None:
        # FIX: Drop NaN values BEFORE calculating
        forecast_clean = pd.concat([actual_demand_series, forecast_series], axis=1).dropna()
        
        if len(forecast_clean) > 0:
            actual = forecast_clean[actual_demand_col]
            forecast = forecast_clean[forecast_col]
            
            # Mean Absolute Percentage Error (MAPE)
            if (actual.abs() > 0).any():
                mape = ((actual - forecast).abs() / actual.abs()).mean() * 100
            else:
                mape = 0
            
            warn_msg = "Poor forecast accuracy (>20%)" if mape > 20 else "None"
            kpis.append(engine.build_kpi(
                category="📊 Demand",
                name="Forecast Accuracy (MAPE)",
                value=f"{mape:.2f}%",
                formula="Mean(|Actual - Forecast| / |Actual|) * 100",
                source=f"`{actual_demand_col}`, `{forecast_col}`",
                warnings=warn_msg
            ))
            
            # Total forecast
            total_forecast = forecast.sum()
            
            kpis.append(engine.build_kpi(
                category="📊 Demand",
                name="Total Forecasted Demand",
                value=f"{total_forecast:,.0f} units",
                formula="Sum(Forecast)",
                source=f"`{forecast_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📊 Demand", "Forecast Accuracy", "Missing valid actual_demand/forecast data."))
    else:
        kpis.append(engine.log_missing("📊 Demand", "Forecast Accuracy", "Missing 'forecasted_demand' column."))
    
    # ==========================================
    # 3. DEMAND BY PRODUCT
    # ==========================================
    if product_col is not None and actual_demand_col is not None:
        product_demand = df.groupby(product_col)[actual_demand_col].sum().sort_values(ascending=False)
        
        if len(product_demand) > 0:
            top_product = product_demand.idxmax()
            top_demand = product_demand.max()
            
            kpis.append(engine.build_kpi(
                category="📊 Demand",
                name="Top Product by Demand",
                value=f"{top_product} ({top_demand:,.0f} units)",
                formula="Product with max demand",
                source=f"`{product_col}`, `{actual_demand_col}`"
            ))
        else:
            kpis.append(engine.log_missing("📊 Demand", "Top Product", "No valid product data."))
    else:
        kpis.append(engine.log_missing("📊 Demand", "Top Product", "Missing 'product_id' column."))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
