import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_freight_metrics(df):
    kpis = []
    if len(df) == 0: return kpis

    weight_col = _first_column(df, ['freight_weight', 'total_weight', 'cargo_weight'])
    damage_col = _first_column(df, ['damage_incidents', 'damaged_goods', 'defect_count'])

    if not weight_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    weight_valid, reason = SemanticValidator.is_valid_duration(df[weight_col].fillna(0))
    if not weight_valid:
        return [{
            "category": "📦 Freight & Cargo", "name": "Total Tonnage Handled",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{weight_col}`",
            "confidence": "Low", "warnings": reason
        }]

    conf, warns = evaluate_kpi_confidence(df, [weight_col, damage_col])
    
    total_weight = df[weight_col].fillna(0).sum()
    kpis.append({
        "category": "📦 Freight & Cargo",
        "name": "Total Tonnage Handled",
        "value": f"{total_weight:,.2f} tons",
        "formula": "SUM(weight)",
        "source": f"`{weight_col}`",
        "confidence": conf,
        "warnings": warns
    })

    if damage_col:
        total_damaged = df[damage_col].fillna(0).sum()
        damage_rate = (total_damaged / len(df)) * 100
        kpis.append({
            "category": "📦 Freight & Cargo",
            "name": "Freight Damage Rate",
            "value": f"{damage_rate:.2f}%",
            "formula": "(COUNT(Damaged) / TOTAL) * 100",
            "source": f"`{damage_col}`",
            "confidence": conf,
            "warnings": "High freight damage detected" if damage_rate > 2 else warns
        })

    return kpis
