"""
Operating cash flow, free cash flow, and runway metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,       
    "score_deduction_for_warning": 20,  
    "low_confidence_threshold": 50,    
}

def calc_cashflow_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    ocf_col, ocf_series = engine.get_numeric(["cash_flow_operating", "ocf", "operating_cash_flow", "operating_cf"])
    capex_col, capex_series = engine.get_numeric(["capital_expenditure", "capex", "capital_investments", "investing_cf"])
    cash_col, cash_series = engine.get_numeric(["cash_balance", "cash", "cash_on_hand", "liquid_cash"])
    burn_col, burn_series = engine.get_numeric(["monthly_burn_rate", "burn_rate", "monthly_burn", "cash_burn"])
    fcf_col, fcf_series = engine.get_numeric(["free_cash_flow", "fcf"])
    
    if ocf_col is None:
        kpis.append(engine.log_missing("💸 Cash Flow", "Cash Flow Metrics", "Missing numeric 'operating_cash_flow'."))
        return kpis
    
    total_ocf = ocf_series.sum()
    kpis.append(engine.build_kpi(
        category="💸 Cash Flow", name="Total Operating Cash Flow",
        value=f"${total_ocf:,.2f}", formula="Sum(OCF)", source=f"`{ocf_col}`",
        warnings="Negative OCF - Cash burn from operations" if total_ocf < 0 else "None"
    ))
    kpis.append(engine.build_kpi(
        category="💸 Cash Flow", name="Avg Monthly OCF",
        value=f"${ocf_series.mean():,.2f}", formula="Mean(OCF)", source=f"`{ocf_col}`"
    ))
    
    # FCF Audit Logic
    if fcf_col is not None:
        total_fcf = fcf_series.sum()
        kpis.append(engine.build_kpi(
            category="💸 Cash Flow", name="Total Free Cash Flow",
            value=f"${total_fcf:,.2f}", formula="Sum(FCF)", source=f"`{fcf_col}`",
            warnings="Negative FCF" if total_fcf < 0 else "None"
        ))
    elif capex_col is not None:
        total_capex = capex_series.sum()
        fcf = total_ocf - abs(total_capex)
        kpis.append(engine.build_kpi(
            category="💸 Cash Flow", name="Free Cash Flow (OCF - CapEx)",
            value=f"${fcf:,.2f}", formula="OCF - CapEx", source=f"`{ocf_col}`, `{capex_col}`",
            warnings="Negative FCF" if fcf < 0 else "None"
        ))
        kpis.append(engine.build_kpi(
            category="💸 Cash Flow", name="Total CapEx",
            value=f"${total_capex:,.2f}", formula="Sum(Capital Expenditures)", source=f"`{capex_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💸 Cash Flow", "Free Cash Flow", "Missing 'fcf' or 'capex' data."))
    
    # Cash Audit Logic
    if cash_col is not None:
        kpis.append(engine.build_kpi(
            category="💸 Cash Flow", name="Total Cash Balance",
            value=f"${cash_series.sum():,.2f}", formula="Sum(Cash)", source=f"`{cash_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="💸 Cash Flow", name="Avg Cash Balance",
            value=f"${cash_series.mean():,.2f}", formula="Mean(Cash)", source=f"`{cash_col}`"
        ))
    else:
        kpis.append(engine.log_missing("💸 Cash Flow", "Cash Balance", "Missing 'cash_balance' column."))
    
    # Runway Audit Logic
    if cash_col is not None and burn_col is not None:
        df_temp = pd.concat([cash_series, burn_series], axis=1).dropna()
        if len(df_temp) > 0:
            avg_cash = cash_series.mean()
            avg_burn = burn_series.mean()
            if avg_burn > 0:
                runway_months = avg_cash / avg_burn
                warn_msg = "CRITICAL: < 6 months runway" if runway_months < 6 else "Low runway - < 12 months" if runway_months < 12 else "None"
                kpis.append(engine.build_kpi(
                    category="💸 Cash Flow", name="Estimated Cash Runway",
                    value=f"{runway_months:.1f} months", formula="Avg Cash / Avg Monthly Burn", 
                    source=f"`{cash_col}`, `{burn_col}`", warnings=warn_msg
                ))
    else:
        kpis.append(engine.log_missing("💸 Cash Flow", "Estimated Runway", "Requires both 'cash' and 'burn_rate' data."))
    
    if enable_debug: engine.print_execution_log()
    return kpis
