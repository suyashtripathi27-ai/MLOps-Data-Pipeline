import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def calc_pharma_sales_metrics(df):
    """
    Computes pharmaceutical sales velocity and class-based market analysis.
    Validates drug class columns (e.g., M01AB, N02BA) to ensure data integrity.
    """
    kpis = []
    if len(df) == 0: return kpis

    # Target the drug class columns identified in your schema sniff
    drug_columns = [col for col in df.columns if col.startswith(('M', 'N', 'R'))]
    
    # 1. Total Sales Volume (Sum of all units sold across all classes)
    total_volume = df[drug_columns].sum().sum()
    
    # 🛡️ ENTERPRISE VALIDATION
    # Ensure the sales data isn't corrupted (e.g., negative units sold)
    valid_volume, reason = SemanticValidator.is_valid_duration(pd.Series([total_volume]))
    if not valid_volume:
        return [{
            "category": "💊 Pharma Sales", "name": "Total Monthly Volume",
            "value": "EXCLUDED", "formula": "N/A", "source": f"Drug Classes",
            "confidence": "Low", "warnings": reason
        }]

    # Calculate Confidence Score based on data completeness
    conf, warns = evaluate_kpi_confidence(df, drug_columns)

    kpis.append({
        "category": "💊 Pharma Sales",
        "name": "Total Units Sold (All Classes)",
        "value": f"{total_volume:,.0f} units",
        "formula": "SUM(ALL_DRUG_CLASSES)",
        "source": f"Class Columns: {len(drug_columns)}",
        "confidence": conf,
        "warnings": warns
    })

    # 2. Market Mix (Top Performing Drug Class)
    class_totals = df[drug_columns].sum()
    top_class = class_totals.idxmax()
    top_class_val = class_totals.max()
    
    kpis.append({
        "category": "💊 Pharma Sales",
        "name": "Top Performing Drug Class",
        "value": f"{top_class} ({top_class_val:,.0f} units)",
        "formula": "MAX(SUM(Class_i))",
        "source": f"Class: {top_class}",
        "confidence": conf,
        "warnings": "High dependency on single class" if (top_class_val / total_volume) > 0.5 else "None"
    })

    return kpis
