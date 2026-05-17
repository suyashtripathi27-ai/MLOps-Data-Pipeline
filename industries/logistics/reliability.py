import pandas as pd

def evaluate_kpi_confidence(df, columns):
    """Evaluates the reliability of columns used for a KPI based on missing data."""
    warnings = []
    confidence = "High"
    
    for col in columns:
        if col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 0:
                warnings.append(f"{missing_pct:.1f}% missing in `{col}`")
                
            if missing_pct >= 20:
                confidence = "Low"
            elif missing_pct > 5 and confidence != "Low":
                confidence = "Medium"
                
    warning_str = ", ".join(warnings) if warnings else "None"
    return confidence, warning_str
