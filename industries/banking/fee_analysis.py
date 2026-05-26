"""
Fee structure and revenue impact KPIs.
"""
import pandas as pd
from utils.kpi_helpers import (
    first_column, safe_kpi, excluded_kpi, confidence_for, safe_exists, safe_numeric, safe_numeric_series
)

def calc_fee_metrics(df):
    kpis = []
    missing_capabilities = []
    if len(df) == 0: return kpis
    
    fee_col = first_column(df, ["fees_charged", "fee_amount", "charges"])
    amount_col = first_column(df, ["amount", "transaction_amount", "revenue"])
    fee_type_col = first_column(df, ["fee_type", "charge_type", "fee_category"])

    conf, warns = confidence_for(df, [fee_col, amount_col, fee_type_col])
    
    if safe_numeric(df, fee_col):
        clean_fee = safe_numeric_series(df, fee_col).fillna(0)
        total_fees = clean_fee.sum()
        
        kpis.append(safe_kpi(
            category="💵 Fee Analysis", name="Total Fee Revenue",
            value=f"${total_fees:,.2f}", formula="Sum(Fees Charged)",
            source=f"`{fee_col}`", confidence=conf, warnings=warns
        ))
        kpis.append(safe_kpi(
            category="💵 Fee Analysis", name="Avg Fee per Transaction",
            value=f"${clean_fee.mean():.2f}", formula="Mean(Fees)",
            source=f"`{fee_col}`", confidence=conf, warnings=warns
        ))

        if safe_numeric(df, amount_col):
            clean_amount = safe_numeric_series(df, amount_col)
            total_amount = clean_amount.sum()
            fee_ratio = (total_fees / total_amount * 100) if total_amount > 0 else 0
            kpis.append(safe_kpi(
                category="💵 Fee Analysis", name="Fee-to-Revenue Ratio",
                value=f"{fee_ratio:.2f}%", formula="Fees / Total Amount * 100",
                source=f"`{fee_col}`, `{amount_col}`", confidence=conf, warnings=warns
            ))
        else:
            missing_capabilities.append("Fee Ratio unavailable: Missing numeric 'amount' column.")

        if safe_exists(df, fee_type_col):
            fee_by_type = clean_fee.groupby(df[fee_type_col]).sum().sort_values(ascending=False)
            if not fee_by_type.empty:
                kpis.append(safe_kpi(
                    category="💵 Fee Analysis", name="Top Fee Category",
                    value=f"{fee_by_type.idxmax()} (${fee_by_type.max():,.2f})", formula="Fee type with max revenue",
                    source=f"`{fee_type_col}`, `{fee_col}`", confidence=conf, warnings=warns
                ))
        else:
            missing_capabilities.append("Fee Category Analytics unavailable: Missing 'fee_type' column.")
    else:
        missing_capabilities.append("Fee Analytics unavailable: Missing numeric 'fee' column.")

    for missing in missing_capabilities:
        kpis.append(excluded_kpi(category="⚠️ System Audit", name="Data Gap Detected", source="Diagnostic", reason=missing))

    return kpis
