"""
Computes retail banking liquidity, overdraft risk, and wealth concentration.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

def calc_balance_metrics(df):
    engine = KPIEngine(df)
    kpis = []
    total_rows = len(df)
    
    if total_rows == 0: 
        return kpis

    bal_col, bal_series = engine.get_numeric(["balance", "account_balance", "ledger_balance"])
    
    if bal_col is not None:
        # 1. Negative Balance Risk (Overdrafts)
        negative_balances = (bal_series < 0).sum()
        negative_rate = (negative_balances / total_rows) * 100

        warn_msg = "High volume of negative balances - Review overdraft policies" if negative_rate > 5 else "None"
        kpis.append(engine.build_kpi(
            category="⚠️ Risk Exposure", name="Accounts in Overdraft (Negative Balance)",
            value=f"{negative_balances:,.0f} ({negative_rate:.2f}%)", formula="COUNT(balance < 0)",
            source=f"`{bal_col}`", warnings=warn_msg
        ))

        # 2. Average Account Balance
        kpis.append(engine.build_kpi(
            category="💰 Balance & Liquidity", name="Average Account Balance",
            value=f"${bal_series.mean():,.2f}", formula="AVG(balance)", source=f"`{bal_col}`"
        ))

        # 3. High-Wealth Concentration Risk (Top 5% of accounts)
        top_5_threshold = bal_series.quantile(0.95)
        top_5_wealth = bal_series[bal_series >= top_5_threshold].sum()
        total_wealth = bal_series.sum()
        concentration_pct = (top_5_wealth / total_wealth * 100) if total_wealth > 0 else 0

        warn_msg = "Severe liquidity concentration risk" if concentration_pct > 60 else "None"
        kpis.append(engine.build_kpi(
            category="💰 Balance & Liquidity", name="Top 5% Account Concentration",
            value=f"{concentration_pct:.1f}% of Total Deposits", formula="SUM(Top 5% Balances) / SUM(All Balances)",
            source=f"`{bal_col}`", warnings=warn_msg
        ))
    else:
        kpis.append(engine.log_missing("💰 Balance & Liquidity", "Balance Metrics", "Missing or invalid 'balance' column."))

    return kpis
