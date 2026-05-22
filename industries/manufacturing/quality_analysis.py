from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _safe_kpi(name, value, formula, source, confidence, warnings):
    return {
        "category": "✅ Quality",
        "name": name,
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warnings": warnings,
    }


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def calc_quality_metrics(df):
    """Calculates defect and yield quality KPIs."""
    kpis = []

    produced_col = _first_column(df, ["units_produced", "production_quantity", "total_units"])
    defect_col = _first_column(df, ["defect_count", "defective_units", "reject_units"])
    scrap_col = _first_column(df, ["scrap_units", "scrap_count"])

    if produced_col:
        produced_valid, produced_reason = SemanticValidator.is_valid_duration(df[produced_col])
        if not produced_valid:
            kpis.append(_safe_kpi("Quality Metrics", "EXCLUDED", "N/A", f"`{produced_col}`", "Low", produced_reason))
            return kpis

    if produced_col and defect_col:
        defect_valid, defect_reason = SemanticValidator.is_valid_duration(df[defect_col])
        if defect_valid:
            total_produced = df[produced_col].dropna().sum()
            total_defects = df[defect_col].dropna().sum()
            if total_produced > 0:
                defect_rate = (total_defects / total_produced) * 100
                conf, warns = evaluate_kpi_confidence(df, [produced_col, defect_col])
                kpis.append(
                    _safe_kpi(
                        "Defect Rate",
                        f"{defect_rate:.2f}%",
                        "(Total Defects / Total Produced) * 100",
                        f"`{defect_col}`, `{produced_col}`",
                        conf,
                        warns,
                    )
                )
                kpis.append(
                    _safe_kpi(
                        "First Pass Yield",
                        f"{(100 - defect_rate):.2f}%",
                        "100 - Defect Rate",
                        f"`{defect_col}`, `{produced_col}`",
                        conf,
                        warns,
                    )
                )
        else:
            kpis.append(_safe_kpi("Defect Rate", "EXCLUDED", "N/A", f"`{defect_col}`", "Low", defect_reason))

    if produced_col and scrap_col:
        scrap_valid, scrap_reason = SemanticValidator.is_valid_duration(df[scrap_col])
        if scrap_valid:
            total_produced = df[produced_col].dropna().sum()
            total_scrap = df[scrap_col].dropna().sum()
            if total_produced > 0:
                conf, warns = evaluate_kpi_confidence(df, [produced_col, scrap_col])
                kpis.append(
                    _safe_kpi(
                        "Scrap Rate",
                        f"{((total_scrap / total_produced) * 100):.2f}%",
                        "(Total Scrap / Total Produced) * 100",
                        f"`{scrap_col}`, `{produced_col}`",
                        conf,
                        warns,
                    )
                )
        else:
            kpis.append(_safe_kpi("Scrap Rate", "EXCLUDED", "N/A", f"`{scrap_col}`", "Low", scrap_reason))

    return kpis
