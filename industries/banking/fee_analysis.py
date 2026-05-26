"""
Fee structure and revenue impact KPIs.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Banking industry configuration
# Stricter than default - regulatory compliance demands accuracy
BANKING_CONFIG = {
    "missing_data_threshold": 5,        # ✅ Stricter than default 10% - banking is risk-sensitive
    "score_deduction_for_warning": 20,  # ✅ Higher penalty for quality issues
    "low_confidence_threshold": 25,     # ✅ Lower threshold = easier to flag as "Low"
}

def calc_fee_metrics(df, enable_debug=False):
    """
    Calculate fee KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """
    # ✅ OPTION 2: Initialize with banking industry config for stricter validation
    engine = KPIEngine(df, industry_config=BANKING_CONFIG)
    
    # ✅ OPTION 1: Enable tracing for enterprise observability
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0: 
        return kpis
    
    fee_col, fee_series = engine.get_numeric(["fees_charged", "fee_amount", "charges"])
    amt_col, amt_series = engine.get_numeric(["amount", "transaction_amount", "revenue"])
    type_col, type_series = engine.get_column(["fee_type", "charge_type", "fee_category"])

    if fee_col is not None:
        clean_fee = fee_series.fillna(0)
        total_fees = clean_fee.sum()
        
        kpis.append(engine.build_kpi(
            category="💵 Fee Analysis", name="Total Fee Revenue",
            value=f"${total_fees:,.2f}", formula="Sum(Fees Charged)", source=f"`{fee_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="💵 Fee Analysis", name="Avg Fee per Transaction",
            value=f"${clean_fee.mean():.2f}", formula="Mean(Fees)", source=f"`{fee_col}`"
        ))

        if amt_col is not None:
            total_amount = amt_series.sum()
            fee_ratio = (total_fees / total_amount * 100) if total_amount > 0 else 0
            kpis.append(engine.build_kpi(
                category="💵 Fee Analysis", name="Fee-to-Revenue Ratio",
                value=f"{fee_ratio:.2f}%", formula="Fees / Total Amount * 100", source=f"`{fee_col}`, `{amt_col}`"
            ))
        else:
            kpis.append(engine.log_missing("💵 Fee Analysis", "Fee Ratio", "Missing numeric 'amount' column."))

        if type_col is not None:
            df_temp = pd.concat([type_series, clean_fee], axis=1).dropna()
            fee_by_type = df_temp.groupby(type_col)[fee_col].sum().sort_values(ascending=False)
            if not fee_by_type.empty:
                kpis.append(engine.build_kpi(
                    category="💵 Fee Analysis", name="Top Fee Category",
                    value=f"{fee_by_type.idxmax()} (${fee_by_type.max():,.2f})", formula="Fee type with max revenue", source=f"`{type_col}`, `{fee_col}`"
                ))
        else:
            kpis.append(engine.log_missing("💵 Fee Analysis", "Fee Category", "Missing 'fee_type' column."))
    else:
        kpis.append(engine.log_missing("💵 Fee Analysis", "Fee Revenue", "Missing numeric 'fee' column."))

    # ✅ OPTION 1: Print execution trace for debugging
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
