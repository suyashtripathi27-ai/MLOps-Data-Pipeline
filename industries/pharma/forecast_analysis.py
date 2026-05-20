import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_forecast_metrics(df):
    """Computes demand planning and supply forecast accuracy."""
    kpis = []
    if len(df) == 0: return kpis

    forecast_col = _first_column(df, ["forecast_demand", "predicted_demand"])
    actual_col = _first_column(df, ["actual_demand", "quantity_sold"])

    if not forecast_col or not actual_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    forecast_valid, reason = SemanticValidator.is_valid_duration(df[forecast_col].fillna(0))
    if not forecast_valid:
        return [{
            "category": "📈 Forecasting & Demand", "name": "Demand Forecast Accuracy",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{forecast_col}`",
            "confidence": "Low", "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [forecast_col, actual_col])
    
    forecast_numeric = df[forecast_col].fillna(0)
    actual_numeric = df[actual_col].fillna(0)
    total_actual = actual_numeric.sum()

    if total_actual > 0:
        # Mean Absolute Percentage Error (MAPE) inverse for accuracy calculation
        absolute_errors = abs(forecast_numeric - actual_numeric)
        mape = (absolute_errors.sum() / total_actual) * 100
        accuracy = max(0, 100 - mape)

        kpis.append({
            "category": "📈 Forecasting & Demand",
            "name": "Demand Forecast Accuracy",
            "value": f"{accuracy:.2f}%",
            "formula": "100 - MAPE(forecast, actual)",
            "source": f"`{forecast_col}`, `{actual_col}`",
            "confidence": conf,
            "warnings": "Severe demand planning variance" if accuracy < 80 else warns
        })

    return kpis
