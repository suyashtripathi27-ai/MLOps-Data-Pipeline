import pandas as pd
import numpy as np

def generate_payload(df):
    """
    Calculates statistics, scores data reliability, and flags extreme outliers.
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
        warnings.append(f"High missing data detected (Some columns > 20% empty).")
        
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
    warning_text = "\n".join([f"- {w}" for w in all_warnings]) if all_warnings else "- None. Data looks statistically stable."
    
    # 4. Bundle into the Enterprise Payload
    return f"""
    [DATA RELIABILITY SCORE]: {max(0, reliability_score)}/100
    
    [SYSTEM WARNINGS & SANITY FLAGS]
    {warning_text}
    
    [DATASET SHAPE]
    Total Rows: {total_rows} | Total Columns: {total_cols}
    
    [STATISTICAL SUMMARY]
    {df.describe(include='all').to_string()}
    """
