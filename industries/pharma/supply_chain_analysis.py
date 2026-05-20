import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_pharma_supply_metrics(df):
    """Computes cold-chain integrity and inventory flow KPIs."""
    kpis = []
    if len(df) == 0: return kpis

    cold_col = _first_column(df, ["cold_chain_breaches", "temp_excursions"])
    stockout_col = _first_column(df, ["stockouts", "out_of_stock_days"])

    if not cold_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    cold_valid, reason = SemanticValidator.is_valid_duration(df[cold_col].fillna(0))
    if not cold_valid:
        return [{
            "category": "❄️ Pharma Supply Chain", "name": "Cold-Chain Integrity",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{cold_col}`",
            "confidence": "Low", "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [cold_col, stockout_col])
    total_breaches = df[cold_col].fillna(0).sum()

    kpis.append({
        "category": "❄️ Pharma Supply Chain",
        "name": "Critical Cold-Chain Breaches",
        "value": f"{total_breaches:,.0f}",
        "formula": "SUM(temp_excursions)",
        "source": f"`{cold_col}`",
        "confidence": conf,
        "warnings": "Product integrity compromised due to temperature" if total_breaches > 0 else warns
    })

    if stockout_col:
        total_stockouts = df[stockout_col].fillna(0).sum()
        kpis.append({
            "category": "❄️ Pharma Supply Chain",
            "name": "Total Stockout Events/Days",
            "value": f"{total_stockouts:,.0f}",
            "formula": "SUM(stockouts)",
            "source": f"`{stockout_col}`",
            "confidence": conf,
            "warnings": "Patient supply continuity at risk" if total_stockouts > 5 else warns
        })

    return kpis
