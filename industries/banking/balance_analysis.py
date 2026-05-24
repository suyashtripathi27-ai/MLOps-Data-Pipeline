"""
Computes retail banking liquidity, overdraft risk, and wealth concentration.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_balance_metrics(df):
    kpis = []
    total_rows = len(df)
    if total_rows == 0: return kpis

    balance_col = first_column(df, ["balance", "account_balance", "ledger_balance"])

    if not balance_col: 
        return kpis

    # Check for numeric data instead of duration
    if not pd.api.types.is_numeric_dtype(df[balance_col]):
        kpis.append(safe_kpi(
            category="💰 Balance & Liquidity", name="Total Deposits",
            value="EXCLUDED", formula="N/A", source=f"`{balance_col}`",
            confidence="Low", warnings="Balance column contains non-numeric data."
        ))
        return kpis

    conf, warns = confidence_for(df, [balance_col])
    
    bal_numeric = pd.to_numeric(df[balance_col], errors='coerce').dropna()
    if bal_numeric.empty: return kpis

    # 1. Negative Balance Risk (Overdrafts)
    negative_balances = (bal_numeric < 0).sum()
    negative_rate = (negative_balances / total_rows) * 100

    kpis.append(safe_kpi(
        category="⚠️ Risk Exposure",
        name="Accounts in Overdraft (Negative Balance)",
        value=f"{negative_balances:,.0f} ({negative_rate:.2f}%)",
        formula="COUNT(balance < 0)",
        source=f"`{balance_col}`",
        confidence=conf,
        warnings="High volume of negative balances - Review overdraft policies" if negative_rate > 5 else warns
    ))

    # 2. Average Account Balance
    avg_balance = bal_numeric.mean()
    kpis.append(safe_kpi(
        category="💰 Balance & Liquidity",
        name="Average Account Balance",
        value=f"${avg_balance:,.2f}",
        formula="AVG(balance)",
        source=f"`{balance_col}`",
        confidence=conf,
        warnings="None"
    ))

    # 3. High-Wealth Concentration Risk (Top 5% of accounts)
    top_5_percent_threshold = bal_numeric.quantile(0.95)
    top_5_wealth = bal_numeric[bal_numeric >= top_5_percent_threshold].sum()
    total_wealth = bal_numeric.sum()
    
    concentration_pct = (top_5_wealth / total_wealth * 100) if total_wealth > 0 else 0

    kpis.append(safe_kpi(
        category="💰 Balance & Liquidity",
        name="Top 5% Account Concentration",
        value=f"{concentration_pct:.1f}% of Total Deposits",
        formula="SUM(Top 5% Balances) / SUM(All Balances)",
        source=f"`{balance_col}`",
        confidence=conf,
        warnings="Severe liquidity concentration risk" if concentration_pct > 60 else "None"
    ))

    return kpis
