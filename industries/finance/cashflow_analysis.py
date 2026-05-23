import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_cashflow_metrics(df):
    """Computes critical liquidity and cash runway metrics for the CFO."""
    kpis = []
    if len(df) == 0: return kpis

    ocf_col = first_column(df, ["cash_flow_operating", "ocf", "operating_cash_flow"])
    capex_col = first_column(df, ["capital_expenditure", "capex", "capital_investments"])
    cash_col = first_column(df, ["cash_balance", "cash_and_equivalents"])
    burn_col = first_column(df, ["monthly_burn_rate", "operating_burn"])

    if not ocf_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    ocf_valid, reason = SemanticValidator.is_valid_duration(df[ocf_col].fillna(0))
    if not ocf_valid:
        return [{
            "category": "💸 Cash Flow & Runway", "name": "Operating Cash Flow",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{ocf_col}`",
            "confidence": "Low", "warnings": reason
        }]

    # Calculate Confidence Score
    conf_cols = [ocf_col] + ([capex_col] if capex_col else []) + ([cash_col] if cash_col else [])
    conf, warns = evaluate_kpi_confidence(df, conf_cols)
    
    # 1. Operating Cash Flow (OCF)
    ocf_numeric = pd.to_numeric(df[ocf_col], errors='coerce').fillna(0)
    total_ocf = ocf_numeric.sum()
    
    kpis.append({
        "category": "💸 Cash Flow & Runway",
        "name": "Total Operating Cash Flow (OCF)",
        "value": f"${total_ocf:,.2f}",
        "formula": "SUM(ocf)",
        "source": f"`{ocf_col}`",
        "confidence": conf,
        "warnings": "Negative OCF indicates core business operations are burning cash" if total_ocf < 0 else warns
    })

    # 2. Free Cash Flow (FCF)
    if capex_col:
        capex_numeric = pd.to_numeric(df[capex_col], errors='coerce').fillna(0)
        total_capex = capex_numeric.sum()
        # Ensure we subtract capex regardless of whether it was recorded as positive or negative
        fcf = total_ocf - abs(total_capex) 
        
        kpis.append({
            "category": "💸 Cash Flow & Runway",
            "name": "Free Cash Flow (FCF)",
            "value": f"${fcf:,.2f}",
            "formula": "OCF - CapEx",
            "source": f"`{ocf_col}`, `{capex_col}`",
            "confidence": conf,
            "warnings": "Severe FCF deficit detected" if fcf < 0 else "None"
        })

    # 3. Cash Runway Estimation
    if cash_col and burn_col:
        # Taking the most recent/average cash balance and burn rate
        avg_cash = pd.to_numeric(df[cash_col], errors='coerce').dropna().mean()
        avg_burn = pd.to_numeric(df[burn_col], errors='coerce').dropna().mean()
        
        if avg_burn > 0:
            runway_months = avg_cash / avg_burn
            kpis.append({
                "category": "💸 Cash Flow & Runway",
                "name": "Estimated Cash Runway",
                "value": f"{runway_months:.1f} months",
                "formula": "Avg Cash Balance / Avg Monthly Burn",
                "source": f"`{cash_col}`, `{burn_col}`",
                "confidence": conf,
                "warnings": "CRITICAL: Less than 6 months of operational runway remaining" if runway_months < 6 else "None"
            })

    return kpis
  
