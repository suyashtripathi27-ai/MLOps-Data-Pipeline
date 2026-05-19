import pandas as pd
from utils.validator import SemanticValidator

def calc_hub_metrics(df):
    """Calculates KPIs for warehousing and distribution centers with validation."""
    kpis = []
    
    # 1. Facility Bottlenecks (Average Detention Time)
    if 'detention_minutes' in df.columns:
        is_valid, reason = SemanticValidator.is_valid_duration(df['detention_minutes'])
        
        if is_valid:
            valid_detention = df['detention_minutes'].dropna()
            if not valid_detention.empty:
                avg_detention = valid_detention.mean()
                kpis.append({
                    "category": "🏢 Hub Operations", "name": "Average Detention Time",
                    "value": f"{avg_detention:.1f} mins",
                    "source": "`detention_minutes`"
                })
        else:
            kpis.append({
                "category": "🏢 Hub Operations", "name": "Average Detention Time",
                "value": "EXCLUDED",
                "source": f"Data rejected: {reason}"
            })

    return kpis
