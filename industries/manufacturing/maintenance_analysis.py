from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _safe_kpi(name, value, formula, source, confidence, warnings):
    return {
        "category": "🛠️ Maintenance",
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


def calc_maintenance_metrics(df):
    """Calculates maintenance and downtime KPIs."""
    kpis = []

    downtime_col = _first_column(df, ["downtime_minutes", "downtime_hours"])
    breakdown_col = _first_column(df, ["breakdown_count", "failure_count"])
    repair_col = _first_column(df, ["repair_time_minutes", "repair_time_hours", "mttr_minutes"])

    if downtime_col:
        valid, reason = SemanticValidator.is_valid_duration(df[downtime_col])
        if valid:
            conf, warns = evaluate_kpi_confidence(df, [downtime_col])
            total_downtime = df[downtime_col].dropna().sum()
            unit = "minutes" if "minute" in downtime_col else "hours"
            kpis.append(
                _safe_kpi(
                    "Total Downtime",
                    f"{total_downtime:,.2f} {unit}",
                    "Sum(downtime)",
                    f"`{downtime_col}`",
                    conf,
                    warns,
                )
            )
        else:
            kpis.append(_safe_kpi("Total Downtime", "EXCLUDED", "N/A", f"`{downtime_col}`", "Low", reason))

    if downtime_col and breakdown_col:
        total_breakdowns = df[breakdown_col].dropna().sum()
        total_downtime = df[downtime_col].dropna().sum()
        if total_breakdowns > 0:
            conf, warns = evaluate_kpi_confidence(df, [downtime_col, breakdown_col])
            kpis.append(
                _safe_kpi(
                    "Downtime per Breakdown",
                    f"{(total_downtime / total_breakdowns):,.2f}",
                    "Total Downtime / Total Breakdowns",
                    f"`{downtime_col}`, `{breakdown_col}`",
                    conf,
                    warns,
                )
            )

    if repair_col:
        repair_valid, repair_reason = SemanticValidator.is_valid_duration(df[repair_col])
        if repair_valid:
            conf, warns = evaluate_kpi_confidence(df, [repair_col])
            kpis.append(
                _safe_kpi(
                    "Mean Time To Repair",
                    f"{df[repair_col].dropna().mean():,.2f}",
                    "Mean(repair_time)",
                    f"`{repair_col}`",
                    conf,
                    warns,
                )
            )
        else:
            kpis.append(_safe_kpi("Mean Time To Repair", "EXCLUDED", "N/A", f"`{repair_col}`", "Low", repair_reason))

    return kpis
