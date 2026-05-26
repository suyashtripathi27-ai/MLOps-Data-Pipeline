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
    """
    Calculate risk KPIs with optional execution tracing.
    
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
    
    return_col, return_series = engine.get_numeric(["return", "roi", "pct_return", "investment_return"])
    volatility_col, volatility_series = engine.get_numeric(["volatility", "std_dev", "variance"])
    risk_score_col, risk_score_series = engine.get_numeric(["risk_score", "risk_rating", "credit_score"])
    default_col, default_series = engine.get_column(["default_flag", "defaulted", "is_default", "loan_default"])
    loss_col, loss_series = engine.get_numeric(["loss", "loss_amount", "expected_loss"])
    
    # Return metrics
    if return_col is not None:
        avg_return = return_series.mean()
        std_return = return_series.std()
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Avg Return %",
            value=f"{avg_return:.2f}%", formula="Mean(Return)", source=f"`{return_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Return Volatility (Std Dev)",
            value=f"{std_return:.2f}%", formula="StdDev(Return)", source=f"`{return_col}`"
        ))
    
    # Risk score
    if risk_score_col is not None:
        avg_risk = risk_score_series.mean()
        high_risk = (risk_score_series > risk_score_series.quantile(0.75)).sum()
        high_risk_pct = (high_risk / len(df) * 100) if len(df) > 0 else 0
        
        warn_msg = "High portfolio risk" if high_risk_pct > 50 else "None"
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Avg Risk Score",
            value=f"{avg_risk:.2f}", formula="Mean(Risk Score)", source=f"`{risk_score_col}`",
            warnings=warn_msg
        ))
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="High Risk Items %",
            value=f"{high_risk_pct:.2f}%", formula="(Risk > 75th Percentile) / Total * 100", 
            source=f"`{risk_score_col}`"
        ))
    
    # Default rate
    if default_col is not None:
        default_mask = default_series.astype(str).str.lower().isin(['1', 'true', 'yes', 'defaulted', 'default'])
        default_count = default_mask.sum()
        default_rate = (default_count / len(df) * 100) if len(df) > 0 else 0
        
        warn_msg = "CRITICAL: High default rate (>5%)" if default_rate > 5 else "Elevated default rate (>2%)" if default_rate > 2 else "None"
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Default Rate %",
            value=f"{default_rate:.2f}%", formula="(Defaulted / Total) * 100", source=f"`{default_col}`",
            warnings=warn_msg
        ))
    
    # Expected loss
    if loss_col is not None:
        total_loss = loss_series.sum()
        avg_loss = loss_series.mean()
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Total Expected Loss",
            value=f"${total_loss:,.2f}", formula="Sum(Loss)", source=f"`{loss_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="⚠️ Risk", name="Avg Expected Loss",
            value=f"${avg_loss:,.2f}", formula="Mean(Loss)", source=f"`{loss_col}`"
        ))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
