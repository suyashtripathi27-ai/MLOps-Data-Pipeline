import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _safe_kpi(name, value, formula, source, confidence, warnings):
    return {
        "category": "🏭 Production",
        "name": name,
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warnings": warnings,
    }


def calc_production_metrics(df):
    """Calculates production throughput and utilization KPIs."""
    kpis = []

    units_col = _first_column(df, ["units_produced", "production_quantity", "output_qty", "good_units"])
    hours_col = _first_column(df, ["production_hours", "operating_hours", "run_hours"])

    if units_col:
        is_valid, reason = SemanticValidator.is_valid_duration(df[units_col])
        if not is_valid:
            kpis.append(_safe_kpi("Total Output", "EXCLUDED", "N/A", f"`{units_col}`", "Low", reason))
            return kpis

        valid_units = df[units_col].dropna()
        if not valid_units.empty:
            conf, warns = evaluate_kpi_confidence(df, [units_col])
            kpis.append(_safe_kpi("Total Output", f"{valid_units.sum():,.0f}", "Sum(units)", f"`{units_col}`", conf, warns))
            kpis.append(_safe_kpi("Average Output", f"{valid_units.mean():,.2f}", "Mean(units)", f"`{units_col}`", conf, warns))

    if units_col and hours_col:
        hrs_valid, hrs_reason = SemanticValidator.is_valid_duration(df[hours_col])
        if hrs_valid:
            total_hours = df[hours_col].dropna().sum()
            total_units = df[units_col].dropna().sum()
            if total_hours > 0:
                conf, warns = evaluate_kpi_confidence(df, [units_col, hours_col])
                kpis.append(
                    _safe_kpi(
                        "Throughput Rate",
                        f"{(total_units / total_hours):,.2f} units/hr",
                        "Sum(units) / Sum(hours)",
                        f"`{units_col}`, `{hours_col}`",
                        conf,
                        warns,
                    )
                )
        else:
            kpis.append(_safe_kpi("Throughput Rate", "EXCLUDED", "N/A", f"`{hours_col}`", "Low", hrs_reason))

    date_col = _first_column(df, ["date", "production_date", "timestamp", "shift_date"])
    if units_col and date_col:
        trend_df = pd.DataFrame(
            {
                "date": pd.to_datetime(df[date_col], errors="coerce"),
                "units": df[units_col],
            }
        ).dropna()
        if not trend_df.empty:
            daily = trend_df.groupby(trend_df["date"].dt.date)["units"].sum().dropna()
            if len(daily) > 1:
                first_day = daily.iloc[0]
                last_day = daily.iloc[-1]
                growth = ((last_day - first_day) / first_day) * 100 if first_day != 0 else 0
                conf, warns = evaluate_kpi_confidence(df, [units_col, date_col])
                kpis.append(
                    _safe_kpi(
                        "Output Growth %",
                        f"{growth:.2f}%",
                        "((Last - First) / First) * 100",
                        f"`{units_col}`, `{date_col}`",
                        conf,
                        warns,
                    )
                )

    return kpis
