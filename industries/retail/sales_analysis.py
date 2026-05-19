import pandas as pd
from utils.validator import SemanticValidator

def calc_sales_metrics(df):
    """Calculates Average Transaction Value and Margins."""
    kpis = []
    
    if 'revenue' in df.columns:
        # 🛡️ GATEKEEPER: Ensure revenue isn't a corrupted negative anomaly
        is_valid, reason = SemanticValidator.is_valid_duration(df['revenue'])
        
        if is_valid:
            valid_rev = df['revenue'].dropna()
            if not valid_rev.empty:
                total_rev = valid_rev.sum()
                atv = valid_rev.mean()
                
                kpis.append({
                    "category": "💰 Sales Performance", "name": "Total Revenue",
                    "value": f"${total_rev:,.2f}",
                    "source": "`revenue`"
                })
                kpis.append({
                    "category": "💰 Sales Performance", "name": "Avg Transaction Value (ATV)",
                    "value": f"${atv:.2f}",
                    "source": "`revenue`"
                })
        else:
            kpis.append({
                "category": "💰 Sales Performance", "name": "Revenue Metrics",
                "value": "EXCLUDED",
                "source": f"Data rejected: {reason}"
            })

    # Profit Margin Calculation
    if 'revenue' in df.columns and 'total_cost' in df.columns:
        rev_valid, _ = SemanticValidator.is_valid_duration(df['revenue'])
        cost_valid, _ = SemanticValidator.is_valid_duration(df['total_cost'])
        
        if rev_valid and cost_valid:
            total_rev = df['revenue'].sum()
            total_cost = df['total_cost'].sum()
            
            if total_rev > 0:
                margin = ((total_rev - total_cost) / total_rev) * 100
                kpis.append({
                    "category": "💰 Sales Performance", "name": "Overall Profit Margin",
                    "value": f"{margin:.1f}%",
                    "source": "`revenue`, `total_cost`"
                })

    return kpis
