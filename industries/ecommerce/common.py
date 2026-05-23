import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator
from utils.confidence_engine import evaluate_kpi_confidence


def first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def safe_kpi(category, name, value, formula, source, confidence, warnings):
    return {
        "category": category,
        "name": name,
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warnings": warnings,
    }


def excluded_kpi(category, name, source, reason):
    return safe_kpi(category, name, "EXCLUDED", "N/A", source, "Low", reason)


def bool_mask(series):
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y", "t"])


def confidence_for(df, columns):
    valid_columns = [column for column in columns if column and column in df.columns]
    if not valid_columns:
        return "Low", "No valid columns available."
    return evaluate_kpi_confidence(df, valid_columns)
