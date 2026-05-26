"""
Financial risk metrics, volatility, and default indicators.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_risk_metrics(df, enable_debug=False):
    engine = KPIEngine(df, industry_config=FINANCE_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    kpis = []
    if len(df) == 0: return kpis
    
    return_col, return_series = engine.get_numeric(["return", "roi", "pct_return", "investment_return"])
    volatility_col, volatility_series = engine.get_numeric(["volatility", "std_dev", "variance"])
    risk_score_col, risk_score_series = engine.get_numeric(["risk_score", "risk_rating", "credit_score"])
    default_col, default_series = engine.get_column(["default_flag", "defaulted", "is_default", "loan_default"])
    loss_col, loss_series = engine.get_numeric(["loss", "loss_amount", "expected_loss"])
    
    if return_col is not None:
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Avg Return %",
            value=f"{return_series.mean():.2f}%", formula="Mean(Return)", source=f"`{return_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Return Volatility (Std Dev)",
            value=f"{return_series.std():.2f}%", formula="StdDev(Return)", source=f"`{return_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⚠️ Risk", "Return & Volatility", "Missing numeric 'return' column."))
    
    if risk_score_col is not None:
        avg_risk = risk_score_series.mean()
        high_risk_pct = ((risk_score_series > risk_score_series.quantile(0.75)).sum() / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Avg Risk Score",
            value=f"{avg_risk:.2f}", formula="Mean(Risk Score)", source=f"`{risk_score_col}`",
            warnings="High portfolio risk" if high_risk_pct > 50 else "None"
        ))
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="High Risk Items %",
            value=f"{high_risk_pct:.2f}%", formula="(Risk > 75th Percentile) / Total * 100", source=f"`{risk_score_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⚠️ Risk", "Risk Scoring", "Missing numeric 'risk_score' column."))
    
    if default_col is not None:
        default_mask = default_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'defaulted', 'default'])
        default_rate = (default_mask.sum() / len(df) * 100) if len(df) > 0 else 0
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Default Rate %",
            value=f"{default_rate:.2f}%", formula="(Defaulted / Total) * 100", source=f"`{default_col}`",
            warnings="CRITICAL: High default rate (>5%)" if default_rate > 5 else "Elevated default rate (>2%)" if default_rate > 2 else "None"
        ))
    else:
        kpis.append(engine.log_missing("⚠️ Risk", "Default Rate", "Missing 'default_flag' column."))
    
    if loss_col is not None:
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Total Expected Loss",
            value=f"${loss_series.sum():,.2f}", formula="Sum(Loss)", source=f"`{loss_col}`"
        ))
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Avg Expected Loss",
            value=f"${loss_series.mean():,.2f}", formula="Mean(Loss)", source=f"`{loss_col}`"
        ))
    else:
        kpis.append(engine.log_missing("⚠️ Risk", "Expected Loss", "Missing numeric 'loss' column."))
    
    if enable_debug: engine.print_execution_log()
    return kpis
