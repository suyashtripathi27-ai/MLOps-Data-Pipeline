import pandas as pd


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def check_negative_sales(df):
    """Flags rows with negative sales/revenue values."""
    sales_col = _first_column(df, ["revenue", "sales", "weekly_sales", "total_sales"])
    if not sales_col:
        return []
    negative_count = int((df[sales_col] < 0).sum())
    if negative_count > 0:
        return [f"⚠️ {negative_count} negative sales values detected in `{sales_col}`."]
    return []


def check_duplicate_transactions(df):
    """Flags duplicate transaction records if ID fields are available."""
    id_col = _first_column(df, ["transaction_id", "order_id", "invoice_id"])
    if not id_col:
        return []
    duplicate_count = int(df[id_col].duplicated().sum())
    if duplicate_count > 0:
        return [f"⚠️ {duplicate_count} duplicate transaction IDs found in `{id_col}`."]
    return []


def check_timestamp_anomalies(df):
    """Flags anomalous timestamps such as pre-2000 or unparseable values."""
    time_col = _first_column(df, ["timestamp", "transaction_date", "order_date", "date"])
    if not time_col:
        return []
    ts = pd.to_datetime(df[time_col], errors="coerce")
    warnings = []
    invalid_count = int(ts.isna().sum())
    if invalid_count > 0:
        warnings.append(f"⚠️ {invalid_count} unparseable timestamp values in `{time_col}`.")
    if ts.notna().any():
        min_year = int(ts.dropna().dt.year.min())
        if min_year < 2000:
            warnings.append(f"⚠️ Timestamp anomaly: minimum year in `{time_col}` is {min_year}.")
    return warnings


def run_retail_governance_checks(df):
    """Runs all governance checks for retail data quality."""
    return (
        check_negative_sales(df)
        + check_duplicate_transactions(df)
        + check_timestamp_anomalies(df)
    )


def evaluate_kpi_confidence(df, columns):
    """Evaluates KPI confidence with missing-data and outlier penalties."""
    warnings = []
    score_deduction = 0

    if len(df) == 0:
        return "Low", "Empty dataframe."

    for col in columns:
        if col and col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 20:
                warnings.append(f"Severe missing data in `{col}` (>20%)")
                score_deduction += 15
            elif missing_pct > 5:
                warnings.append(f"Moderate missing data in `{col}` (>5%)")
                score_deduction += 5

            if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
                max_val = df[col].max()
                if pd.notnull(max_val):
                    q99 = df[col].quantile(0.99)
                    if max_val > (q99 * 5) and q99 > 0:
                        warnings.append(f"Severe outliers in `{col}`")
                        score_deduction += 10

    governance_warnings = run_retail_governance_checks(df)
    if governance_warnings:
        score_deduction += min(30, 5 * len(governance_warnings))
        warnings.extend(governance_warnings)

    confidence = "High"
    if score_deduction >= 25:
        confidence = "Low"
    elif score_deduction > 0:
        confidence = "Medium"

    warning_str = ", ".join(warnings) if warnings else "None"
    return confidence, warning_str
