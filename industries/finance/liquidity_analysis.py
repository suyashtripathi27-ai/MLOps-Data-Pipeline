"""
Liquidity ratios, solvency, and balance sheet health metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_liquidity_metrics(df, enable_debug=False):
    """
    Calculate liquidity and solvency KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    
    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    current_assets_col, current_assets_series = engine.get_numeric(["current_assets", "liquid_assets", "cash_and_equivalents"])
    current_liab_col, current_liab_series = engine.get_numeric(["current_liabilities", "short_term_debt", "accounts_payable"])
    asset_col, asset_series = engine.get_numeric(["total_assets", "assets"])
    debt_col, debt_series = engine.get_numeric(["total_debt", "debt_amount", "liabilities", "total_liabilities"])
    equity_col, equity_series = engine.get_numeric(["equity", "shareholders_equity", "net_worth"])
    cash_col, cash_series = engine.get_numeric(["cash", "cash_balance", "cash_on_hand"])
    
    if asset_col is None and debt_col is None:
        kpis.append(engine.log_missing("⚖️ Liquidity & Solvency", "Balance Sheet", "Missing 'total_assets' or 'total_debt'."))
        return kpis
    
    # Current ratio
    if current_assets_col is not None and current_liab_col is not None:
        total_ca = current_assets_series.sum()
        total_cl = current_liab_series.sum()
        current_ratio = (total_ca / total_cl) if total_cl > 0 else 0
        
        warn_msg = "CRITICAL: Liquidity crisis (<1.0)" if current_ratio < 1.0 else "Low liquidity (<1.5)" if current_ratio < 1.5 else "None"
        kpis.append(engine.build_kpi(
            category="⚖️ Liquidity & Solvency", name="Current Ratio",
            value=f"{current_ratio:.2f}x", formula="Current Assets / Current Liabilities", 
            source=f"`{current_assets_col}`, `{current_liab_col}`",
            warnings=warn_msg
        ))
    
    # Quick ratio
    if current_assets_col is not None and current_liab_col is not None and cash_col is not None:
        total_ca = current_assets_series.sum()
        total_cash = cash_series.sum()
        total_cl = current_liab_series.sum()
        quick_assets = total_cash  # Simplification: cash as quick assets
        quick_ratio = (quick_assets / total_cl) if total_cl > 0 else 0
        
        warn_msg = "CRITICAL: No liquid coverage (<0.5)" if quick_ratio < 0.5 else "None"
        kpis.append(engine.build_kpi(
            category="⚖️ Liquidity & Solvency", name="Quick Ratio",
            value=f"{quick_ratio:.2f}x", formula="Quick Assets / Current Liabilities", 
            source=f"`{cash_col}`, `{current_liab_col}`",
            warnings=warn_msg
        ))
    
    # Debt-to-equity
    if debt_col is not None and equity_col is not None:
        total_debt = debt_series.sum()
        total_equity = equity_series.sum()
        debt_to_equity = (total_debt / total_equity) if total_equity > 0 else 0
        
        warn_msg = "High leverage (>2.0x)" if debt_to_equity > 2.0 else "None"
        kpis.append(engine.build_kpi(
            category="⚖️ Liquidity & Solvency", name="Debt-to-Equity Ratio",
            value=f"{debt_to_equity:.2f}x", formula="Total Debt / Total Equity", 
            source=f"`{debt_col}`, `{equity_col}`",
            warnings=warn_msg
        ))
    
    # Asset coverage
    if asset_col is not None and debt_col is not None:
        total_assets = asset_series.sum()
        total_debt = debt_series.sum()
        asset_coverage = (total_assets / total_debt) if total_debt > 0 else 0
        
        warn_msg = "CRITICAL: Insolvency risk (<1.0x)" if asset_coverage < 1.0 else "None"
        kpis.append(engine.build_kpi(
            category="⚖️ Liquidity & Solvency", name="Asset Coverage Ratio",
            value=f"{asset_coverage:.2f}x", formula="Total Assets / Total Debt", 
            source=f"`{asset_col}`, `{debt_col}`",
            warnings=warn_msg
        ))
    
    # Equity ratio
    if equity_col is not None and asset_col is not None:
        total_equity = equity_series.sum()
        total_assets = asset_series.sum()
        equity_ratio = (total_equity / total_assets * 100) if total_assets > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="⚖️ Liquidity & Solvency", name="Equity Ratio %",
            value=f"{equity_ratio:.2f}%", formula="(Total Equity / Total Assets) * 100", 
            source=f"`{equity_col}`, `{asset_col}`"
        ))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
