import pandas as pd


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def check_negative_values(df):
    warnings = []
    for col in ["revenue", "sales", "order_value", "price", "unit_price", "discount_amount", "shipping_cost", "quantity", "cart_value"]:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            neg_count = int((df[col] < 0).sum())
            if neg_count > 0:
                warnings.append(f"⚠️ {neg_count} negative values found in `{col}`.")
    return warnings


def check_duplicate_orders(df):
    warnings = []
    order_col = _first_column(df, ["order_id", "transaction_id", "invoice_id", "cart_id"])
    if not order_col:
        return warnings
    duplicate_count = int(df[order_col].duplicated().sum())
    if duplicate_count > 0:
        warnings.append(f"⚠️ {duplicate_count} duplicate IDs found in `{order_col}`.")
    return warnings


def check_timestamp_anomalies(df):
    warnings = []
    time_col = _first_column(df, ["timestamp", "transaction_date", "order_date", "date", "session_start", "session_date"])
    if not time_col:
        return warnings
    ts = pd.to_datetime(df[time_col], errors="coerce")
    invalid_count = int(ts.isna().sum())
    if invalid_count > 0:
        warnings.append(f"⚠️ {invalid_count} unparseable timestamp values in `{time_col}`.")
    if ts.notna().any():
        min_year = int(ts.dropna().dt.year.min())
        if min_year < 2000:
            warnings.append(f"⚠️ Timestamp anomaly: minimum year in `{time_col}` is {min_year}.")
    return warnings


def check_rate_bounds(df):
    warnings = []
    for col in ["conversion_rate", "bounce_rate", "cart_abandonment_rate", "return_rate", "refund_rate", "fraud_rate", "cancel_rate"]:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            min_val = df[col].min()
            max_val = df[col].max()
            if min_val < 0 or max_val > 100:
                warnings.append(f"⚠️ Out-of-bounds percentage values found in `{col}`.")
    return warnings


def run_ecommerce_governance_checks(df):
    return check_negative_values(df) + check_duplicate_orders(df) + check_timestamp_anomalies(df) + check_rate_bounds(df)


def evaluate_kpi_confidence(df, columns):
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
                    if pd.notnull(q99) and q99 > 0 and max_val > (q99 * 5):
                        warnings.append(f"Severe outliers in `{col}`")
                        score_deduction += 10

    governance_warnings = run_ecommerce_governance_checks(df)
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
