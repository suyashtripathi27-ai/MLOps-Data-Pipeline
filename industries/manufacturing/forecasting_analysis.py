import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence

def calc_forecasting_metrics(df):
    """Compute demand and forecast accuracy KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    forecast_col = first_column(df, ["forecast_units", "forecast_volume", "predicted_demand"])
    actual_col = first_column(df, ["actual_units", "actual_demand", "realized_demand"])

    if forecast_col and pd.api.types.is_numeric_dtype(df[forecast_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [forecast_col])
        kpis.append({
            "category": "📈 Forecasting",
            "name": "Forecasted Volume",
            "value": f"{df[forecast_col].sum():,.0f} units",
            "formula": f"SUM({forecast_col})",
            "source": forecast_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if forecast_col and actual_col and pd.api.types.is_numeric_dtype(df[forecast_col]) and pd.api.types.is_numeric_dtype(df[actual_col]):
        forecast_total = df[forecast_col].sum()
        actual_total = df[actual_col].sum()
        accuracy = (1 - abs(actual_total - forecast_total) / actual_total) * 100 if actual_total else 0
        confidence, warnings = evaluate_kpi_confidence(df, [forecast_col, actual_col])
        kpis.append({
            "category": "📈 Forecasting",
            "name": "Forecast Accuracy",
            "value": f"{accuracy:,.2f}%",
            "formula": "1 - ABS(actual - forecast) / actual",
            "source": f"{forecast_col}, {actual_col}",
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
