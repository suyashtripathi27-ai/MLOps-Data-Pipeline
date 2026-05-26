"""
Profitability margins and earnings metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_profitability_metrics(df, enable_debug=False):
    """
    Calculate profitability KPIs with optional execution tracing.
    
    Args:
        df: Input DataFrame
        enable_debug: If True, prints execution trace log for observability
    
    Returns:
        List of KPI dictionaries
    """

    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    revenue_col, revenue_series = engine.get_numeric(["revenue", "sales", "gross_revenue", "income", "turnover"])
    net_col, net_series = engine.get_numeric(["net_income", "net_profit", "bottom_line", "net_earnings"])
    ebitda_col, ebitda_series = engine.get_numeric(["ebitda", "operating_profit_before_depreciation", "ebit"])
    gross_profit_col, gross_profit_series = engine.get_numeric(["gross_profit", "gross_margin", "gross_income"])
    
    if revenue_col is None:
        kpis.append(engine.log_missing("💰 Profitability & Margins", "Revenue Metrics", "Missing numeric 'revenue'."))
        return kpis
    
    # Revenue
    total_revenue = revenue_series.sum()
    avg_revenue = revenue_series.mean()
    
    kpis.append(engine.build_kpi(
        category="💰 Profitability & Margins", name="Total Revenue",
        value=f"${total_revenue:,.2f}", formula="Sum(Revenue)", source=f"`{revenue_col}`"
    ))
    
    kpis.append(engine.build_kpi(
        category="💰 Profitability & Margins", name="Avg Revenue",
        value=f"${avg_revenue:,.2f}", formula="Mean(Revenue)", source=f"`{revenue_col}`"
    ))
    
    # Net income & margin
    if net_col is not None:
        total_net = net_series.sum()
        net_margin = (total_net / total_revenue * 100) if total_revenue > 0 else 0
        
        warn_msg = "Negative profitability" if total_net < 0 else "None"
        kpis.append(engine.build_kpi(
            category="💰 Profitability & Margins", name="Total Net Income",
            value=f"${total_net:,.2f}", formula="Sum(Net Income)", source=f"`{net_col}`",
            warnings=warn_msg
        ))
        
        warn_msg = "Low net margin (<5%)" if net_margin < 5 else "None"
        kpis.append(engine.build_kpi(
            category="💰 Profitability & Margins", name="Net Profit Margin %",
            value=f"{net_margin:.2f}%", formula="(Net Income / Revenue) * 100", source=f"`{net_col}`, `{revenue_col}`",
            warnings=warn_msg
        ))
    
    # Gross profit & margin
    if gross_profit_col is not None:
        total_gross = gross_profit_series.sum()
        gross_margin = (total_gross / total_revenue * 100) if total_revenue > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="💰 Profitability & Margins", name="Total Gross Profit",
            value=f"${total_gross:,.2f}", formula="Sum(Gross Profit)", source=f"`{gross_profit_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="💰 Profitability & Margins", name="Gross Profit Margin %",
            value=f"{gross_margin:.2f}%", formula="(Gross Profit / Revenue) * 100", source=f"`{gross_profit_col}`, `{revenue_col}`"
        ))
    
    # EBITDA
    if ebitda_col is not None:
        total_ebitda = ebitda_series.sum()
        ebitda_margin = (total_ebitda / total_revenue * 100) if total_revenue > 0 else 0
        
        kpis.append(engine.build_kpi(
            category="💰 Profitability & Margins", name="Total EBITDA",
            value=f"${total_ebitda:,.2f}", formula="Sum(EBITDA)", source=f"`{ebitda_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="💰 Profitability & Margins", name="EBITDA Margin %",
            value=f"{ebitda_margin:.2f}%", formula="(EBITDA / Revenue) * 100", source=f"`{ebitda_col}`, `{revenue_col}`"
        ))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
