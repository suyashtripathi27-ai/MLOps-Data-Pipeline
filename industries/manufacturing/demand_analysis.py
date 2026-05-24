"""
Demand planning, forecast accuracy, and demand patterns.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_demand_metrics(df):
    """Calculates demand planning KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Demand is COUNT (quantity), not time
    actual_demand_col = first_column(df, ["actual_demand", "orders_received", "sales_volume"])
    forecast_col = first_column(df, ["forecasted_demand", "predicted_demand", "planned_demand"])
    date_col = first_column(df, ["date", "period", "month"])
    product_col = first_column(df, ["product_id", "product", "sku"])
    
    if not actual_demand_col:
        return kpis
    
    # Demand is quantity (COUNT), not duration
    if not pd.api.types.is_numeric_dtype(df[actual_demand_col]):
        kpis.append(safe_kpi(
            category="📊 Demand",
            name="Demand Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{actual_demand_col}`",
            confidence="Low",
            warnings="Demand column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [actual_demand_col, forecast_col, date_col, product_col] if col])
    
    # Total demand
    total_demand = df[actual_demand_col].sum()
    avg_demand = df[actual_demand_col].mean()
    
    kpis.append(safe_kpi(
        category="📊 Demand",
        name="Total Actual Demand",
        value=f"{total_demand:,.0f} units",
        formula="Sum(Actual Demand)",
        source=f"`{actual_demand_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="📊 Demand",
        name="Avg Demand per Period",
        value=f"{avg_demand:,.0f} units",
        formula="Mean(Actual Demand)",
        source=f"`{actual_demand_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Forecast accuracy
    if forecast_col and pd.api.types.is_numeric_dtype(df[forecast_col]):
        valid_df = df.dropna(subset=[actual_demand_col, forecast_col])
        
        if not valid_df.empty:
            actual = valid_df[actual_demand_col]
            forecast = valid_df[forecast_col]
            
            # Mean Absolute Percentage Error (MAPE)
            mape = ((actual - forecast).abs() / actual.abs()).mean() * 100 if (actual.abs() > 0).any() else 0
            
            kpis.append(safe_kpi(
                category="📊 Demand",
                name="Forecast Accuracy (MAPE)",
                value=f"{mape:.2f}%",
                formula="Mean(|Actual - Forecast| / |Actual|) * 100",
                source=f"`{actual_demand_col}`, `{forecast_col}`",
                confidence=conf,
                warnings="Poor forecast accuracy" if mape > 20 else warns
            ))
            
            # Total forecast
            total_forecast = forecast.sum()
            
            kpis.append(safe_kpi(
                category="📊 Demand",
                name="Total Forecasted Demand",
                value=f"{total_forecast:,.0f} units",
                formula="Sum(Forecast)",
                source=f"`{forecast_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Demand by product
    if product_col:
        product_demand = df.groupby(product_col)[actual_demand_col].sum().sort_values(ascending=False)
        
        if not product_demand.empty:
            top_product = product_demand.idxmax()
            top_demand = product_demand.max()
            
            kpis.append(safe_kpi(
                category="📊 Demand",
                name="Top Product by Demand",
                value=f"{top_product} ({top_demand:,.0f} units)",
                formula="Product with max demand",
                source=f"`{product_col}`, `{actual_demand_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
