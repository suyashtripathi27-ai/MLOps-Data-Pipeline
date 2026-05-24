"""
Liquidity ratios, solvency, and balance sheet health metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_liquidity_metrics(df):
    """Calculates liquidity and solvency KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    current_assets_col = first_column(df, ["current_assets", "liquid_assets", "cash_and_equivalents"])
    current_liab_col = first_column(df, ["current_liabilities", "short_term_debt", "accounts_payable"])
    asset_col = first_column(df, ["total_assets", "assets"])
    debt_col = first_column(df, ["total_debt", "debt_amount", "liabilities", "total_liabilities"])
    equity_col = first_column(df, ["equity", "shareholders_equity", "net_worth"])
    cash_col = first_column(df, ["cash", "cash_balance", "cash_on_hand"])
    
    if not asset_col and not debt_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [asset_col, debt_col, equity_col, current_assets_col, current_liab_col] if col])
    
    # Total assets
    if asset_col and pd.api.types.is_numeric_dtype(df[asset_col]):
        total_assets = df[asset_col].sum()
        
        kpis.append(safe_kpi(
            category="⚖️ Liquidity & Solvency",
            name="Total Assets",
            value=f"${total_assets:,.2f}",
            formula="Sum(Assets)",
            source=f"`{asset_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Current ratio
    if current_assets_col and current_liab_col and pd.api.types.is_numeric_dtype(df[current_assets_col]) and pd.api.types.is_numeric_dtype(df[current_liab_col]):
        total_current_assets = df[current_assets_col].sum()
        total_current_liab = df[current_liab_col].sum()
        
        current_ratio = (total_current_assets / total_current_liab) if total_current_liab > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚖️ Liquidity & Solvency",
            name="Current Ratio",
            value=f"{current_ratio:.2f}x",
            formula="Current Assets / Current Liabilities",
            source=f"`{current_assets_col}`, `{current_liab_col}`",
            confidence=conf,
            warnings="Below 1.0x - Liquidity crisis risk" if current_ratio < 1.0 else "Low ratio - Monitor" if current_ratio < 1.5 else warns
        ))
    
    # Debt to equity ratio
    if debt_col and equity_col and pd.api.types.is_numeric_dtype(df[debt_col]) and pd.api.types.is_numeric_dtype(df[equity_col]):
        total_debt = df[debt_col].sum()
        total_equity = df[equity_col].sum()
        
        dte_ratio = (total_debt / total_equity) if total_equity > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚖️ Liquidity & Solvency",
            name="Debt-to-Equity Ratio",
            value=f"{dte_ratio:.2f}x",
            formula="Total Debt / Total Equity",
            source=f"`{debt_col}`, `{equity_col}`",
            confidence=conf,
            warnings="Highly leveraged (>2.0x)" if dte_ratio > 2.0 else warns
        ))
    
    # Debt to assets ratio
    if debt_col and asset_col and pd.api.types.is_numeric_dtype(df[debt_col]) and pd.api.types.is_numeric_dtype(df[asset_col]):
        total_debt = df[debt_col].sum()
        total_assets = df[asset_col].sum()
        
        dta_ratio = (total_debt / total_assets * 100) if total_assets > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚖️ Liquidity & Solvency",
            name="Debt-to-Assets Ratio",
            value=f"{dta_ratio:.2f}%",
            formula="(Total Debt / Total Assets) * 100",
            source=f"`{debt_col}`, `{asset_col}`",
            confidence=conf,
            warnings="Over-leveraged (>60%)" if dta_ratio > 60 else warns
        ))
    
    # Asset coverage ratio
    if asset_col and debt_col and pd.api.types.is_numeric_dtype(df[asset_col]) and pd.api.types.is_numeric_dtype(df[debt_col]):
        total_assets = df[asset_col].sum()
        total_debt = df[debt_col].sum()
        
        asset_coverage = (total_assets / total_debt) if total_debt > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚖️ Liquidity & Solvency",
            name="Asset Coverage Ratio",
            value=f"{asset_coverage:.2f}x",
            formula="Total Assets / Total Debt",
            source=f"`{asset_col}`, `{debt_col}`",
            confidence=conf,
            warnings="CRITICAL: Insolvency risk (< 1.0x)" if asset_coverage < 1.0 else warns
        ))
    
    # Equity ratio
    if equity_col and asset_col and pd.api.types.is_numeric_dtype(df[equity_col]) and pd.api.types.is_numeric_dtype(df[asset_col]):
        total_equity = df[equity_col].sum()
        total_assets = df[asset_col].sum()
        
        equity_ratio = (total_equity / total_assets * 100) if total_assets > 0 else 0
        
        kpis.append(safe_kpi(
            category="⚖️ Liquidity & Solvency",
            name="Equity Ratio",
            value=f"{equity_ratio:.2f}%",
            formula="(Total Equity / Total Assets) * 100",
            source=f"`{equity_col}`, `{asset_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
