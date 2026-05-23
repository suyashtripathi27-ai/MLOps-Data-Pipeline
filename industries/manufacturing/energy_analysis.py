import pandas as pd
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_energy_metrics(df):
    """Compute energy consumption and intensity KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    energy_col = _first_column(df, ["energy_kwh", "power_consumption_kwh", "electricity_kwh"])
    intensity_col = _first_column(df, ["energy_intensity", "kwh_per_unit"])
    gas_col = _first_column(df, ["gas_usage", "gas_consumption", "steam_usage"])

    if energy_col and pd.api.types.is_numeric_dtype(df[energy_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [energy_col])
        kpis.append({
            "category": "🔌 Energy",
            "name": "Total Electricity Usage",
            "value": f"{df[energy_col].sum():,.1f} kWh",
            "formula": f"SUM({energy_col})",
            "source": energy_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if intensity_col and pd.api.types.is_numeric_dtype(df[intensity_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [intensity_col])
        kpis.append({
            "category": "🔌 Energy",
            "name": "Average Energy Intensity",
            "value": f"{df[intensity_col].mean():,.2f}",
            "formula": f"AVG({intensity_col})",
            "source": intensity_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    if gas_col and pd.api.types.is_numeric_dtype(df[gas_col]):
        confidence, warnings = evaluate_kpi_confidence(df, [gas_col])
        kpis.append({
            "category": "🔌 Energy",
            "name": "Total Gas / Thermal Usage",
            "value": f"{df[gas_col].sum():,.1f}",
            "formula": f"SUM({gas_col})",
            "source": gas_col,
            "confidence": confidence,
            "warnings": warnings,
        })

    return kpis
