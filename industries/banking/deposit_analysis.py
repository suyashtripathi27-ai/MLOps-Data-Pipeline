"""
Deposit-specific KPIs (savings, checking, term deposits).
"""
import pandas as pd
from utils.kpi_helpers import (
    first_column, safe_kpi, excluded_kpi, confidence_for, safe_exists, safe_numeric, safe_numeric_series
)

def calc_deposit_metrics(df):
    kpis = []
    missing_capabilities = []
    if len(df) == 0: return kpis
    
    product_col = first_column(df, ["product_type", "product_name", "account_type"])
    amount_col = first_column(df, ["amount", "balance", "deposit_amount"])
    interest_col = first_column(df, ["interest_earned", "interest_income", "interest_rate"])

    conf, warns = confidence_for(df, [product_col, amount_col, interest_col])
    
    if safe_exists(df, product_col) and safe_numeric(df, amount_col):
        clean_amount = safe_numeric_series(df, amount_col)
        product_summary = clean_amount.groupby(df[product_col]).sum().sort_values(ascending=False)

        if not product_summary.empty:
            total_deposits = product_summary.sum()
            top_product = product_summary.idxmax()
            top_product_share = (product_summary.max() / total_deposits * 100) if total_deposits > 0 else 0

            kpis.append(safe_kpi(
                category="🏦 Deposit Analysis", name="Total Deposit Amount",
                value=f"${total_deposits:,.2f}", formula="Sum(Deposit Amount)",
                source=f"`{product_col}`, `{amount_col}`", confidence=conf, warnings=warns
            ))
            kpis.append(safe_kpi(
                category="🏦 Deposit Analysis", name="Top Deposit Product",
                value=f"{top_product} ({top_product_share:.2f}%)", formula="Product with max deposits",
                source=f"`{product_col}`, `{amount_col}`", confidence=conf, warnings=warns
            ))
            kpis.append(safe_kpi(
                category="🏦 Deposit Analysis", name="Deposit Product Count",
                value=f"{len(product_summary)}", formula="Count(Distinct Products)",
                source=f"`{product_col}`", confidence=conf, warnings=warns
            ))
    else:
        missing_capabilities.append("Product valuation unavailable: Requires 'product' and numeric 'amount'.")

    if safe_numeric(df, interest_col):
        clean_interest = safe_numeric_series(df, interest_col)
        kpis.append(safe_kpi(
            category="🏦 Deposit Analysis", name="Total Interest",
            value=f"${clean_interest.sum():,.2f}", formula="Sum(Interest)",
            source=f"`{interest_col}`", confidence=conf, warnings=warns
        ))
        kpis.append(safe_kpi(
            category="🏦 Deposit Analysis", name="Avg Interest Rate",
            value=f"{clean_interest.mean():.2f}%", formula="Mean(Interest Rate)",
            source=f"`{interest_col}`", confidence=conf, warnings=warns
        ))
    else:
        missing_capabilities.append("Interest Analytics unavailable: Missing numeric 'interest' column.")

    for missing in missing_capabilities:
        kpis.append(excluded_kpi(category="⚠️ System Audit", name="Data Gap Detected", source="Diagnostic", reason=missing))

    return kpis
