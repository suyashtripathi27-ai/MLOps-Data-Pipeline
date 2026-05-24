"""
Profitability, margins, and EBITDA metrics for financial analysis.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_profitability_metrics(df):
    """Calculates profitability and margin KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    revenue_col = first_column(df, ["revenue", "sales", "gross_revenue", "income", "turnover"])
    net_col = first_column(df, ["net_income", "net_profit", "bottom_line", "net_earnings"])
    ebitda_col = first_column(df, ["ebitda", "operating_profit_before_depreciation", "ebit"])
    gross_profit_col = first_column(df, ["gross_profit", "gross_margin", "gross_income"])
    
    if not revenue_col:
        return kpis
    
    # Revenue is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[revenue_col]):
        kpis.append(safe_kpi(
            category="💰 Profitability & Margins",
            name="Revenue Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{revenue_col}`",
            confidence="Low",
            warnings="Revenue column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [revenue_col, net_col, ebitda_col, gross_profit_col] if col])
    
    # Total revenue
    total_revenue = df[revenue_col].sum()
    
    kpis.append(safe_kpi(
        category="💰 Profitability & Margins",
        name="Total Revenue",
        value=f"${total_revenue:,.2f}",
        formula="Sum(Revenue)",
        source=f"`{revenue_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Gross profit margin
    if gross_profit_col and pd.api.types.is_numeric_dtype(df[gross_profit_col]) and total_revenue > 0:
        total_gross = df[gross_profit_col].sum()
        gross_margin = (total_gross / total_revenue) * 100
        
        kpis.append(safe_kpi(
            category="💰 Profitability & Margins",
            name="Gross Profit Margin",
            value=f"{gross_margin:.2f}%",
            formula="(Gross Profit / Revenue) * 100",
            source=f"`{gross_profit_col}`, `{revenue_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Net profit margin
    if net_col and pd.api.types.is_numeric_dtype(df[net_col]) and total_revenue > 0:
        total_net = df[net_col].sum()
        net_margin = (total_net / total_revenue) * 100
        
        kpis.append(safe_kpi(
            category="💰 Profitability & Margins",
            name="Net Profit Margin",
            value=f"{net_margin:.2f}%",
            formula="(Net Income / Revenue) * 100",
            source=f"`{net_col}`, `{revenue_col}`",
            confidence=conf,
            warnings="Critical margin compression" if net_margin < 5 else warns
        ))
        
        kpis.append(safe_kpi(
            category="💰 Profitability & Margins",
            name="Total Net Income",
            value=f"${total_net:,.2f}",
            formula="Sum(Net Income)",
            source=f"`{net_col}`",
            confidence=conf,
            warnings="Negative net income" if total_net < 0 else warns
        ))
    
    # EBITDA
    if ebitda_col and pd.api.types.is_numeric_dtype(df[ebitda_col]):
        total_ebitda = df[ebitda_col].sum()
        
        kpis.append(safe_kpi(
            category="💰 Profitability & Margins",
            name="Total EBITDA",
            value=f"${total_ebitda:,.2f}",
            formula="Sum(EBITDA)",
            source=f"`{ebitda_col}`",
            confidence=conf,
            warnings="Negative EBITDA - Cash burn" if total_ebitda < 0 else warns
        ))
        
        # EBITDA margin
        if total_revenue > 0:
            ebitda_margin = (total_ebitda / total_revenue) * 100
            
            kpis.append(safe_kpi(
                category="💰 Profitability & Margins",
                name="EBITDA Margin",
                value=f"{ebitda_margin:.2f}%",
                formula="(EBITDA / Revenue) * 100",
                source=f"`{ebitda_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
