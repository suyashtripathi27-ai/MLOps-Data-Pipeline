"""
Account-level deposit and balance trend KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

def calc_account_metrics(df):
    engine = KPIEngine(df)
    kpis = []
    
    if len(df) == 0: 
        return kpis

    # 1. Grab the Data (The Engine handles routing, safety, coercion, AND tracks columns!)
    acct_col, acct_series = engine.get_column(["account_id", "account_number", "acct_id"])
    amt_col, amt_series = engine.get_numeric(["amount", "transaction_amount", "value"])
    bal_col, bal_series = engine.get_numeric(["balance", "account_balance", "ending_balance"])
    date_col, date_series = engine.get_datetime(["transaction_date", "date", "posting_date"])
    
    # ==========================================
    # 1. ACCOUNT ACTIVITY
    # ==========================================
    if acct_col is not None:
        kpis.append(engine.build_kpi(
            category="💳 Account Analysis", name="Total Active Accounts",
            value=f"{acct_series.nunique():,}", formula="Count(Distinct Account IDs)", source=f"`{acct_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💳 Account Analysis", "Active Accounts", "Missing 'account_id' column."))

    # ==========================================
    # 2. TRANSACTION VOLUME
    # ==========================================
    if amt_col is not None:
        kpis.append(engine.build_kpi(
            category="💳 Account Analysis", name="Total Transaction Volume",
            value=f"${amt_series.sum():,.2f}", formula="Sum(Amount)", source=f"`{amt_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="💳 Account Analysis", name="Avg Transaction Size",
            value=f"${amt_series.mean():,.2f}", formula="Mean(Amount)", source=f"`{amt_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💳 Account Analysis", "Transaction Volume", "Missing or invalid 'amount' column."))

    # ==========================================
    # 3. BALANCE HEALTH
    # ==========================================
    if bal_col is not None:
        kpis.append(engine.build_kpi(
            category="💳 Account Analysis", name="Avg Account Balance",
            value=f"${bal_series.mean():,.2f}", formula="Mean(Balance)", source=f"`{bal_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="💳 Account Analysis", name="Min Account Balance",
            value=f"${bal_series.min():,.2f}", formula="Min(Balance)", source=f"`{bal_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💳 Account Analysis", "Balance Metrics", "Missing or invalid 'balance' column."))

    # ==========================================
    # 4. TRENDS & GROWTH
    # ==========================================
    if date_col is not None and amt_col is not None:
        # Re-sync the clean series by index to group them properly
        df_temp = pd.concat([date_series, amt_series], axis=1).dropna()
        monthly_volume = df_temp.groupby(pd.Grouper(key=date_col, freq='ME'))[amt_col].sum()
        
        if len(monthly_volume) >= 2:
            first_val, last_val = monthly_volume.iloc[0], monthly_volume.iloc[-1]
            growth = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            kpis.append(engine.build_kpi(
                category="💳 Account Analysis", name="Account Growth %",
                value=f"{growth:.2f}%", formula="((Last - First) / First) * 100", source=f"`{amt_col}`, `{date_col}`"
            ))
    else:
        kpis.append(engine.log_missing("💳 Account Analysis", "Account Growth", "Requires valid 'date' and 'amount'."))

    return kpis
