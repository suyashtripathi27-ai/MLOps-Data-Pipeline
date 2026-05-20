import pandas as pd
from .reliability import evaluate_kpi_confidence
from utils.validator import SemanticValidator

def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns: return col
    return None

def calc_liquidity_solvency_metrics(df):
    """Computes balance sheet health, leverage, and liquidity risk."""
    kpis = []
    if len(df) == 0: return kpis

    asset_col = _first_column(df, ["asset_value", "total_assets", "assets", "portfolio_value"])
    debt_col = _first_column(df, ["debt_amount", "total_debt", "liabilities"])
    equity_col = _first_column(df, ["equity_amount", "total_equity", "shareholder_equity"])

    if not asset_col and not debt_col: 
        return kpis

    # 🛡️ ENTERPRISE VALIDATION
    validation_col = asset_col if asset_col else debt_col
    valid_check, reason = SemanticValidator.is_valid_duration(df[validation_col].fillna(0))
    if not valid_check:
        return [{
            "category": "⚖️ Liquidity & Solvency", "name": "Balance Sheet Health",
            "value": "EXCLUDED", "formula": "N/A", "source": f"`{validation_col}`",
            "confidence": "Low", "warnings": reason
        }]

    # Calculate Confidence Score
    conf_cols = [asset_col, debt_col, equity_col]
    conf, warns = evaluate_kpi_confidence(df, conf_cols)
    
    # 1. Total Assets
    if asset_col:
        asset_numeric = pd.to_numeric(df[asset_col], errors='coerce').fillna(0)
        total_assets = asset_numeric.sum()
        kpis.append({
            "category": "⚖️ Liquidity & Solvency",
            "name": "Total Asset Value",
            "value": f"${total_assets:,.2f}",
            "formula": "SUM(assets)",
            "source": f"`{asset_col}`",
            "confidence": conf,
            "warnings": warns
        })

    # 2. Debt-to-Equity Ratio (Leverage)
    if debt_col and equity_col:
        debt_numeric = pd.to_numeric(df[debt_col], errors='coerce').fillna(0)
        equity_numeric = pd.to_numeric(df[equity_col], errors='coerce').fillna(0)
        
        total_debt = debt_numeric.sum()
        total_equity = equity_numeric.sum()
        
        if total_equity > 0:
            dte_ratio = total_debt / total_equity
            kpis.append({
                "category": "⚖️ Liquidity & Solvency",
                "name": "Debt-to-Equity (D/E) Ratio",
                "value": f"{dte_ratio:.2f}x",
                "formula": "Total Debt / Total Equity",
                "source": f"`{debt_col}`, `{equity_col}`",
                "confidence": conf,
                "warnings": "Highly leveraged: D/E ratio exceeds 2.0x" if dte_ratio > 2.0 else "None"
            })

    # 3. Asset-to-Debt Coverage (Solvency)
    if asset_col and debt_col:
        asset_numeric = pd.to_numeric(df[asset_col], errors='coerce').fillna(0)
        debt_numeric = pd.to_numeric(df[debt_col], errors='coerce').fillna(0)
        
        total_assets = asset_numeric.sum()
        total_debt = debt_numeric.sum()
        
        if total_debt > 0:
            coverage = total_assets / total_debt
            kpis.append({
                "category": "⚖️ Liquidity & Solvency",
                "name": "Asset-to-Debt Coverage",
                "value": f"{coverage:.2f}x",
                "formula": "Total Assets / Total Debt",
                "source": f"`{asset_col}`, `{debt_col}`",
                "confidence": conf,
                "warnings": "CRITICAL: Technical insolvency risk (Assets < Liabilities)" if coverage < 1.0 else "None"
            })

    return kpis
