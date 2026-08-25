import pandas as pd

def evaluate_kpi_confidence(df, columns, custom_industry_checks=None):
    """
    UNIVERSAL CONFIDENCE SCORER.
    Checks for missing data across any dataset, and applies optional industry-specific rules.
    """
    warnings = []
    score_deduction = 0

    if len(df) == 0:
        return "Low", "Empty dataframe."
import pandas as pd

def evaluate_kpi_confidence(df, columns, custom_industry_checks=None):
    """
    UNIVERSAL CONFIDENCE SCORER.
    Checks for missing data across any dataset, and applies optional industry-specific rules.
    """
    warnings = []
    score_deduction = 0

    if len(df) == 0:
        return "Low", "Empty dataframe."

    # Universal Check: Missing Data
    for col in columns:
        if col and col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 10:
                warnings.append(f"Missing data in `{col}` (>10%)")
                score_deduction += 15

            # Universal Check: Bulk outlier contamination (distinct from a rare
            # individual outlier). A column with zero missing values can still be
            # unreliable if a large chunk of it consists of extreme sentinel or
            # corrupted values sitting many orders of magnitude above the rest —
            # e.g. a "rate" column that should be 0-1 but has ~30% of rows at
            # ~1e9 due to a known data-entry/placeholder artifact. Sum/Mean on
            # such a column is dominated by the contaminated rows, not the real
            # data, but a pure missing-data check would never catch it.
            if pd.api.types.is_numeric_dtype(df[col]):
                series = df[col].dropna()
                if len(series) > 0:
                    q1, q3 = series.quantile(0.25), series.quantile(0.75)
                    iqr = q3 - q1
                    if iqr > 0:
                        upper_fence = q3 + (3 * iqr)
                        extreme_frac = (series > upper_fence).mean()
                        if extreme_frac > 0.05:
                            warnings.append(
                                f"`{col}`: {extreme_frac*100:.1f}% of values are extreme "
                                f"outliers relative to the rest of the column — sums/means "
                                f"for this metric are likely dominated by anomalous or "
                                f"corrupted data rather than reflecting typical values"
                            )
                            score_deduction += 40
                        elif extreme_frac > 0.01:
                            warnings.append(
                                f"`{col}`: {extreme_frac*100:.1f}% of values are extreme "
                                f"outliers — treat sums/means with caution"
                            )
                            score_deduction += 20

                    # Mean-vs-median distortion check — catches HEAVY contamination
                    # (>25% of rows) that the IQR check above misses entirely, because
                    # a contamination fraction that large drags Q1/Q3 themselves into
                    # the corrupted range, making the IQR fence too loose to trigger.
                    # The median stays robust up to ~50% contamination, so a mean that
                    # is orders of magnitude away from the median is a reliable signal
                    # that Sum/Mean on this column is meaningless, regardless of what
                    # fraction of rows are actually responsible.
                    median = series.median()
                    mean = series.mean()
                    if abs(median) > 1e-9 and abs(mean) / abs(median) > 100:
                        warnings.append(
                            f"`{col}`: mean ({mean:,.4g}) is {abs(mean)/abs(median):,.0f}x "
                            f"the median ({median:,.4g}) — this column is likely dominated "
                            f"by a large block of anomalous or corrupted values, not just a "
                            f"few rare outliers; Sum/Mean should not be treated as reliable"
                        )
                        score_deduction += 40

    # Inject specific checks (e.g., negative downtime in manufacturing, negative age in HR)
    if custom_industry_checks:
        industry_warnings = custom_industry_checks(df)
        if industry_warnings:
            score_deduction += min(40, 10 * len(industry_warnings))
            warnings.extend(industry_warnings)

    # Calculate final baseline
    confidence = "High"
    if score_deduction >= 30:
        confidence = "Low"
    elif score_deduction > 0:
        confidence = "Medium"

    return confidence, ", ".join(warnings) if warnings else "None"
    # Universal Check: Missing Data
    for col in columns:
        if col and col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 10:
                warnings.append(f"Missing data in `{col}` (>10%)")
                score_deduction += 15

    # Inject specific checks (e.g., negative downtime in manufacturing, negative age in HR)
    if custom_industry_checks:
        industry_warnings = custom_industry_checks(df)
        if industry_warnings:
            score_deduction += min(40, 10 * len(industry_warnings))
            warnings.extend(industry_warnings)

    # Calculate final baseline
    confidence = "High"
    if score_deduction >= 30:
        confidence = "Low"
    elif score_deduction > 0:
        confidence = "Medium"

    return confidence, ", ".join(warnings) if warnings else "None"
