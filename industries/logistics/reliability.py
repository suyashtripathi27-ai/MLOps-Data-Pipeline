import pandas as pd

def evaluate_kpi_confidence(df, columns):
    """Evaluates column reliability and returns an auditable penalty log."""
    warnings = []
    score_deduction = 0
    
    for col in columns:
        if col in df.columns:
            # 1. Missing Data Penalty
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 20:
                warnings.append(f"Severe missing data in `{col}` (>20%)")
                score_deduction += 15
            elif missing_pct > 5:
                warnings.append(f"Moderate missing data in `{col}` (>5%)")
                score_deduction += 5
                
            # 2. Outlier/Corruption Penalty (Basic Sanity Check)
            if pd.api.types.is_numeric_dtype(df[col]):
                max_val = df[col].max()
                if pd.notnull(max_val):
                    q99 = df[col].quantile(0.99)
                    if max_val > (q99 * 5) and q99 > 0:
                         warnings.append(f"Severe outliers in `{col}`")
                         score_deduction += 10
                         
    # Calculate final column-level confidence
    confidence = "High"
    if score_deduction >= 20:
        confidence = "Low"
    elif score_deduction > 0:
        confidence = "Medium"
        
    warning_str = ", ".join(warnings) if warnings else "None"
    return confidence, warning_str
