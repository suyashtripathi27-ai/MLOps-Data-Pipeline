"""
Operating cash flow, free cash flow, and runway metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_cashflow_metrics(df):
    """Calculates cash flow and runway KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    ocf_col = first_column(df, ["cash_flow_operating", "ocf", "operating_cash_flow", "operating_cf"])
    capex_col = first_column(df, ["capital_expenditure", "capex", "capital_investments", "investing_cf"])
    cash_col = first_column(df, ["cash_balance", "cash", "cash_on_hand", "liquid_cash"])
    burn_col = first_column(df, ["monthly_burn_rate", "burn_rate", "monthly_burn", "cash_burn"])
    fcf_col = first_column(df, ["free_cash_flow", "fcf"])
    
    if not ocf_col:
        return kpis
    
    # OCF is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[ocf_col]):
        kpis.append(safe_kpi(
            category="💸 Cash Flow",
            name="Cash Flow Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{ocf_col}`",
            confidence="Low",
            warnings="OCF column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [ocf_col, capex_col, cash_col, burn_col, fcf_col] if col])
    
    # Operating cash flow
    total_ocf = df[ocf_col].sum()
    avg_ocf = df[ocf_col].mean()
    
    kpis.append(safe_kpi(
        category="💸 Cash Flow",
        name="Total Operating Cash Flow",
        value=f"${total_ocf:,.2f}",
        formula="Sum(OCF)",
        source=f"`{ocf_col}`",
        confidence=conf,
        warnings="Negative OCF - Cash burn from operations" if total_ocf < 0 else warns
    ))
    
    kpis.append(safe_kpi(
        category="💸 Cash Flow",
        name="Avg Monthly OCF",
        value=f"${avg_ocf:,.2f}",
        formula="Mean(OCF)",
        source=f"`{ocf_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Free cash flow
    if fcf_col and pd.api.types.is_numeric_dtype(df[fcf_col]):
        total_fcf = df[fcf_col].sum()
        
        kpis.append(safe_kpi(
            category="💸 Cash Flow",
            name="Total Free Cash Flow",
            value=f"${total_fcf:,.2f}",
            formula="Sum(FCF)",
            source=f"`{fcf_col}`",
            confidence=conf,
            warnings="Negative FCF" if total_fcf < 0 else warns
        ))
    elif capex_col and pd.api.types.is_numeric_dtype(df[capex_col]):
        total_capex = df[capex_col].sum()
        fcf = total_ocf - abs(total_capex)
        
        kpis.append(safe_kpi(
            category="💸 Cash Flow",
            name="Free Cash Flow (OCF - CapEx)",
            value=f"${fcf:,.2f}",
            formula="OCF - CapEx",
            source=f"`{ocf_col}`, `{capex_col}`",
            confidence=conf,
            warnings="Negative FCF" if fcf < 0 else warns
        ))
        
        kpis.append(safe_kpi(
            category="💸 Cash Flow",
            name="Total CapEx",
            value=f"${total_capex:,.2f}",
            formula="Sum(Capital Expenditures)",
            source=f"`{capex_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Cash balance
    if cash_col and pd.api.types.is_numeric_dtype(df[cash_col]):
        total_cash = df[cash_col].sum()
        avg_cash = df[cash_col].mean()
        
        kpis.append(safe_kpi(
            category="💸 Cash Flow",
            name="Total Cash Balance",
            value=f"${total_cash:,.2f}",
            formula="Sum(Cash)",
            source=f"`{cash_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💸 Cash Flow",
            name="Avg Cash Balance",
            value=f"${avg_cash:,.2f}",
            formula="Mean(Cash)",
            source=f"`{cash_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Runway estimation
    if cash_col and burn_col and pd.api.types.is_numeric_dtype(df[cash_col]) and pd.api.types.is_numeric_dtype(df[burn_col]):
        valid_cash = df[cash_col].dropna()
        valid_burn = df[burn_col].dropna()
        
        if not valid_cash.empty and not valid_burn.empty:
            avg_cash = valid_cash.mean()
            avg_burn = valid_burn.mean()
            
            if avg_burn > 0:
                runway_months = avg_cash / avg_burn
                
                kpis.append(safe_kpi(
                    category="💸 Cash Flow",
                    name="Estimated Cash Runway",
                    value=f"{runway_months:.1f} months",
                    formula="Avg Cash / Avg Monthly Burn",
                    source=f"`{cash_col}`, `{burn_col}`",
                    confidence=conf,
                    warnings="CRITICAL: < 6 months runway" if runway_months < 6 else "Low runway - < 12 months" if runway_months < 12 else warns
                ))
    
    return kpis
