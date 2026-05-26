"""
Account-level deposit and balance trend KPIs.
"""
import pandas as pd
from utils.kpi_helpers import (
    first_column, 
    safe_kpi, 
    excluded_kpi, 
    confidence_for, 
    safe_exists, 
    safe_numeric, 
    safe_datetime
)

def calc_account_metrics(df):
    """Calculates account performance and balance health KPIs."""
    kpis = []
    missing_capabilities = [] # 🛡️ The Audit Tracker
    
    if len(df) == 0:
        return kpis

    account_col = first_column(df, ["account_id", "account_number", "acct_id"])
    amount_col = first_column(df, ["amount", "transaction_amount", "value"])
    balance_col = first_column(df, ["balance", "account_balance", "ending_balance"])
    date_col = first_column(df, ["transaction_date", "date", "posting_date"])

    conf, warns = confidence_for(df, [col for col in [account_col, amount_col, balance_col, date_col] if col])
    
    # ==========================================
    # 1. ACCOUNT ACTIVITY (Requires Account ID)
    # ==========================================
    if safe_exists(df, account_col):
        account_activity = df[account_col].nunique()
        kpis.append(safe_kpi(
            category="💳 Account Analysis", name="Total Active Accounts",
            value=f"{account_activity:,}", formula="Count(Distinct Account IDs)",
            source=f"`{account_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("Active accounts unavailable: Missing 'account_id' column.")

    # ==========================================
    # 2. TRANSACTION VOLUME (Requires Numeric Amount)
    # ==========================================
    if safe_numeric(df, amount_col):
        total_volume = df[amount_col].sum()
        avg_transaction = df[amount_col].mean()
        
        kpis.append(safe_kpi(
            category="💳 Account Analysis", name="Total Transaction Volume",
            value=f"${total_volume:,.2f}", formula="Sum(Amount)",
            source=f"`{amount_col}`", confidence=conf, warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💳 Account Analysis", name="Avg Transaction Size",
            value=f"${avg_transaction:,.2f}", formula="Mean(Amount)",
            source=f"`{amount_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("Transaction volume unavailable: Missing or invalid 'amount' column.")

    # ==========================================
    # 3. BALANCE HEALTH (Requires Numeric Balance)
    # ==========================================
    if safe_numeric(df, balance_col):
        avg_balance = df[balance_col].mean()
        min_balance = df[balance_col].min()
        
        kpis.append(safe_kpi(
            category="💳 Account Analysis", name="Avg Account Balance",
            value=f"${avg_balance:,.2f}", formula="Mean(Balance)",
            source=f"`{balance_col}`", confidence=conf, warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💳 Account Analysis", name="Min Account Balance",
            value=f"${min_balance:,.2f}", formula="Min(Balance)",
            source=f"`{balance_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("Balance metrics unavailable: Missing or invalid 'balance' column.")

    # ==========================================
    # 4. TRENDS & GROWTH (Requires Date + Amount)
    # ==========================================
    if safe_datetime(df, date_col) and safe_numeric(df, amount_col):
        df_temp = df.dropna(subset=[date_col, amount_col]).copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors="coerce")
        
        monthly_volume = df_temp.groupby(pd.Grouper(key=date_col, freq='ME'))[amount_col].sum()
        
        if len(monthly_volume) >= 2:
            first_val = monthly_volume.iloc[0]
            last_val = monthly_volume.iloc[-1]
            growth = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            
            kpis.append(safe_kpi(
                category="💳 Account Analysis", name="Account Growth %",
                value=f"{growth:.2f}%", formula="((Last Month - First Month) / First) * 100",
                source=f"`{amount_col}`, `{date_col}`", confidence=conf, warnings=warns
            ))
    else:
        missing_capabilities.append("Trend analytics unavailable: Requires valid 'date' and 'amount' columns.")

    # ==========================================
    # 5. TRANSPARENCY AUDIT TRAIL
    # ==========================================
    for missing in missing_capabilities:
        kpis.append(excluded_kpi(
            category="⚠️ System Audit", 
            name="Data Gap Detected", 
            source="Diagnostic", 
            reason=missing
        ))

    return kpis
