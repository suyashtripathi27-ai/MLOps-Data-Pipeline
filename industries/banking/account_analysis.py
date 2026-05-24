"""
Account-level deposit and balance trend KPIs.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_account_metrics(df):
    """Calculates account performance and balance health KPIs."""
    kpis = []
    if len(df) == 0:
        return kpis

    account_col = first_column(df, ["account_id", "account_number", "acct_id"])
    amount_col = first_column(df, ["amount", "transaction_amount", "value"])
    balance_col = first_column(df, ["balance", "account_balance", "ending_balance"])
    date_col = first_column(df, ["transaction_date", "date", "posting_date"])

    if not account_col or not amount_col:
        return kpis

    # Ensure amount is numeric (removed the buggy is_valid_duration check)
    if not pd.api.types.is_numeric_dtype(df[amount_col]):
        kpis.append(safe_kpi(
            category="💳 Account Analysis",
            name="Account Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{amount_col}`",
            confidence="Low",
            warnings="Amount column contains non-numeric data."
        ))
        return kpis

    # Correctly use your imported confidence_for wrapper
    conf, warns = confidence_for(df, [account_col, amount_col])
    
    account_activity = df[account_col].nunique()
    total_volume = df[amount_col].sum()
    avg_transaction = df[amount_col].mean()

    # Use safe_kpi instead of raw dictionaries!
    kpis.append(safe_kpi(
        category="💳 Account Analysis",
        name="Total Active Accounts",
        value=f"{account_activity}",
        formula="Count(Distinct Account IDs)",
        source=f"`{account_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="💳 Account Analysis",
        name="Total Transaction Volume",
        value=f"${total_volume:,.2f}",
        formula="Sum(Amount)",
        source=f"`{amount_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="💳 Account Analysis",
        name="Avg Transaction Size",
        value=f"${avg_transaction:,.2f}",
        formula="Mean(Amount)",
        source=f"`{amount_col}`",
        confidence=conf,
        warnings=warns
    ))

    if balance_col and pd.api.types.is_numeric_dtype(df[balance_col]):
        avg_balance = df[balance_col].mean()
        min_balance = df[balance_col].min()
        
        kpis.append(safe_kpi(
            category="💳 Account Analysis",
            name="Avg Account Balance",
            value=f"${avg_balance:,.2f}",
            formula="Mean(Balance)",
            source=f"`{balance_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        kpis.append(safe_kpi(
            category="💳 Account Analysis",
            name="Min Account Balance",
            value=f"${min_balance:,.2f}",
            formula="Min(Balance)",
            source=f"`{balance_col}`",
            confidence=conf,
            warnings=warns
        ))

    if date_col:
        date_series = pd.to_datetime(df[date_col], errors="coerce")
        date_valid, _ = SemanticValidator.is_valid_datetime(date_series.dropna())
        
        if date_valid and df[date_col].notna().any():
            # Ensure date column is datetime for grouping
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors="coerce")
            
            monthly_volume = df_temp.groupby(pd.Grouper(key=date_col, freq='ME'))[amount_col].sum()
            
            if len(monthly_volume) >= 2:
                first_val = monthly_volume.iloc[0]
                last_val = monthly_volume.iloc[-1]
                growth = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
                
                kpis.append(safe_kpi(
                    category="💳 Account Analysis",
                    name="Account Growth %",
                    value=f"{growth:.2f}%",
                    formula="((Last Month - First Month) / First Month) * 100",
                    source=f"`{amount_col}`, `{date_col}`",
                    confidence=conf,
                    warnings=warns
                ))

    return kpis
