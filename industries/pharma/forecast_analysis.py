"""
Demand forecasting, forecast accuracy, and demand planning metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_forecast_metrics(df):
    """Calculates demand forecasting accuracy KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    # Forecast metrics are COUNT (units), not time
    actual_col = first_column(df, ["actual_demand", "actual_sales", "actual_units"])
    forecast_col = first_column(df, ["forecasted_demand", "predicted_demand", "forecast_units"])
    product_col = first_column(df, ["product_id", "product", "drug_name"])
    period_col = first_column(df, ["period", "month", "quarter"])
    
    if not actual_col or not forecast_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [actual_col, forecast_col, product_col, period_col] if col])
    
    valid_df = df.dropna(subset=[actual_col, forecast_col])
    
    if valid_df.empty:
        return kpis
    
    # Forecast accuracy (MAPE)
    actual = valid_df[actual_col]
    forecast = valid_df[forecast_col]
    
    mape = ((actual - forecast).abs() / actual.abs()).mean() * 100 if (actual.abs() > 0).any() else 0
    
    kpis.append(safe_kpi(
        category="📊 Demand Planning",
        name="Forecast Accuracy (MAPE)",
        value=f"{mape:.2f}%",
        formula="Mean(|Actual - Forecast| / |Actual|) * 100",
        source=f"`{actual_col}`, `{forecast_col}`",
        confidence=conf,
        warnings="Poor forecast accuracy" if mape > 20 else warns
    ))
    
    # Forecast bias
    bias = (forecast - actual).mean()
    
    kpis.append(safe_kpi(
        category="📊 Demand Planning",
        name="Forecast Bias",
        value=f"{bias:,.0f} units",
        formula="Mean(Forecast - Actual)",
        source=f"`{actual_col}`, `{forecast_col}`",
        confidence=conf,
        warnings="Systematic over-forecast" if bias > 0 else "Systematic under-forecast" if bias < 0 else warns
    ))
    
    # By product accuracy
    if product_col:
        product_mape = valid_df.groupby(product_col).apply(
            lambda x: ((x[actual_col] - x[forecast_col]).abs() / x[actual_col].abs()).mean() * 100
        ).sort_values(ascending=False)
        
        if not product_mape.empty:
            worst_product = product_mape.idxmax()
            worst_mape = product_mape.max()
            
            kpis.append(safe_kpi(
                category="📊 Demand Planning",
                name="Worst Forecast Accuracy (by Product)",
                value=f"{worst_product} (MAPE: {worst_mape:.2f}%)",
                formula="Product with highest MAPE",
                source=f"`{product_col}`, `{actual_col}`, `{forecast_col}`",
                confidence=conf,
                warnings="Critical accuracy issue for this product" if worst_mape > 40 else warns
            ))
    
    return kpis
