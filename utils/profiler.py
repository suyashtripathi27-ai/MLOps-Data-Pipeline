import pandas as pd
import numpy as np

def generate_payload(df, industry_context="generic"):
    """
    Calculates statistics, scores data reliability, and flags extreme outliers.
    Returns a dictionary for flawless LLM API JSON integration.
    """
    print("📊 Generating statistical payload & sanity checks...")
    
    # 1. Base Metrics
    total_rows = len(df)
    total_cols = len(df.columns)
    
    # 2. Data Reliability Engine (Starts at 100)
    reliability_score = 100
    warnings = []
    
    # Check 1: Missing Data Penalty
    missing_percent = (df.isnull().sum() / total_rows) * 100
    if missing_percent.max() > 20:
        reliability_score -= 20
        warnings.append("High missing data detected (Some columns > 20% empty).")
        
    # 3. Statistical Sanity Validator
    numeric_cols = df.select_dtypes(include=['number']).columns
    sanity_flags = []
    
    for col in numeric_cols:
        mean_val = df[col].mean()
        std_val = df[col].std()
        max_val = df[col].max()
        
        # Flag Extreme Variance (StdDev is 3x higher than Mean)
        if pd.notnull(std_val) and pd.notnull(mean_val) and mean_val > 0:
            if std_val > (mean_val * 3):
                reliability_score -= 10
                sanity_flags.append(f"[{col}] Extreme variance: Standard deviation is heavily distorted relative to the mean.")
        
        # Flag Extreme Outliers (Max is 5x higher than 99th percentile)
        if pd.notnull(max_val):
            q99 = df[col].quantile(0.99)
            if max_val > (q99 * 5) and q99 > 0:
                reliability_score -= 10
                sanity_flags.append(f"[{col}] Severe outlier: Max value significantly exceeds the 99th percentile.")
                
    # Format the warnings
    all_warnings = warnings + sanity_flags
    if not all_warnings:
        all_warnings = ["None. Data looks statistically stable."]
        
    # 4. Bundle into the Enterprise JSON Payload
    # We convert describe() to a dictionary so the pipeline can parse it cleanly
    stats_dict = df.describe().to_dict()
    clean_stats = {}
    for col, metrics in stats_dict.items():
        clean_stats[col] = {k: round(v, 2) if pd.notnull(v) else None for k, v in metrics.items()}
        
    payload = {
        "dataset_context": industry_context,
        "data_reliability_score": max(0, reliability_score),
        "system_warnings": all_warnings,
        "dataset_shape": {
            "total_rows": total_rows,
            "total_columns": total_cols
        },
        "statistical_summary": clean_stats
    }
    
    return payload
