import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_profitability_metrics(df):
    """Computes high-level CFO profitability metrics (Margins, EBITDA)."""
    kpis = []
    total_rows = len(df)
    if total_rows == 0: return kpis

    rev_col = first_column(df, ["revenue", "sales", "gross_revenue", "income"])
    net_col = first_column(df, ["net_income", "net_profit", "bottom_line"])
    ebitda_col = first_column(df, ["ebitda", "operating_profit_before_depreciation"])

    if not rev_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    # (Assuming your SemanticValidator uses this pattern based on previous modules)
    rev_valid, reason = SemanticValidator.is_valid_duration(df[rev_col].fillna(0))
    if not rev_valid:
        return [{
            "category": "💰 Profitability & Margins", "name": "Total Gross Revenue",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{rev_col}`",
            "confidence": "Low", "warnings": reason
        }]

    # Calculate Confidence Score
    conf_cols = [rev_col] + ([net_col] if net_col else []) + ([ebitda_col] if ebitda_col else [])
    conf, warns = evaluate_kpi_confidence(df, conf_cols)
    
    # 1. Total Revenue
    rev_numeric = pd.to_numeric(df[rev_col], errors='coerce').fillna(0)
    total_rev = rev_numeric.sum()
    
    kpis.append({
        "category": "💰 Profitability & Margins",
        "name": "Total Recognized Revenue",
        "value": f"${total_rev:,.2f}",
        "formula": "SUM(revenue)",
        "source": f"`{rev_col}`",
        "confidence": conf,
        "warnings": warns
    })

    # 2. Net Profit Margin
    if net_col and total_rev > 0:
        net_numeric = pd.to_numeric(df[net_col], errors='coerce').fillna(0)
        total_net = net_numeric.sum()
        net_margin = (total_net / total_rev) * 100
        
        kpis.append({
            "category": "💰 Profitability & Margins",
            "name": "Net Profit Margin",
            "value": f"{net_margin:.2f}%",
            "formula": "(SUM(net_income) / SUM(revenue)) * 100",
            "source": f"`{net_col}`, `{rev_col}`",
            "confidence": conf,
            "warnings": "Critical margin compression detected" if net_margin < 5 else warns
        })

    # 3. EBITDA 
    if ebitda_col:
        ebitda_numeric = pd.to_numeric(df[ebitda_col], errors='coerce').fillna(0)
        total_ebitda = ebitda_numeric.sum()
        
        kpis.append({
            "category": "💰 Profitability & Margins",
            "name": "Total EBITDA",
            "value": f"${total_ebitda:,.2f}",
            "formula": "SUM(ebitda)",
            "source": f"`{ebitda_col}`",
            "confidence": conf,
            "warnings": "Negative EBITDA signals severe operational cash burn" if total_ebitda < 0 else "None"
        })

    return kpis
