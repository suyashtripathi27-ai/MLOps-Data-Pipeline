"""
Investment portfolio performance and allocation metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

FINANCE_CONFIG = {
    "missing_data_threshold": 3,
    "score_deduction_for_warning": 20,
    "low_confidence_threshold": 50,
}

def calc_investment_metrics(df, enable_debug=False):
    """
    Calculate investment KPIs with optional execution tracing.
    
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
    
    investment_col, investment_series = engine.get_numeric(["investment_value", "portfolio_value", "market_value", "investmentamount"])
    return_col, return_series = engine.get_numeric(["return", "roi", "pct_return", "investment_return"])
    allocation_col, allocation_series = engine.get_column(["asset_type", "allocation", "category", "class"])
    
    # Portfolio value
    if investment_col is not None:
        total_portfolio = investment_series.sum()
        avg_investment = investment_series.mean()
        
        kpis.append(engine.build_kpi(
            category="📊 Investment Portfolio", name="Total Portfolio Value",
            value=f"${total_portfolio:,.2f}", formula="Sum(Investment Value)", source=f"`{investment_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📊 Investment Portfolio", name="Avg Investment Size",
            value=f"${avg_investment:,.2f}", formula="Mean(Investment Value)", source=f"`{investment_col}`"
        ))
    
    # Returns
    if return_col is not None:
        avg_return = return_series.mean()
        max_return = return_series.max()
        min_return = return_series.min()
        
        kpis.append(engine.build_kpi(
            category="📊 Investment Portfolio", name="Avg Return %",
            value=f"{avg_return:.2f}%", formula="Mean(Return)", source=f"`{return_col}`"
        ))
        
        kpis.append(engine.build_kpi(
            category="📊 Investment Portfolio", name="Max Return %",
            value=f"{max_return:.2f}%", formula="Max(Return)", source=f"`{return_col}`"
        ))
        
        warn_msg = "Negative returns" if min_return < 0 else "None"
        kpis.append(engine.build_kpi(
            category="📊 Investment Portfolio", name="Min Return %",
            value=f"{min_return:.2f}%", formula="Min(Return)", source=f"`{return_col}`",
            warnings=warn_msg
        ))
    
    # Allocation diversification
    if allocation_col is not None:
        allocation_dist = df[allocation_col].value_counts()
        num_allocations = len(allocation_dist)
        
        kpis.append(engine.build_kpi(
            category="📊 Investment Portfolio", name="Asset Classes",
            value=f"{num_allocations}", formula="Count(Distinct Allocations)", source=f"`{allocation_col}`"
        ))
        
        if num_allocations > 0:
            top_allocation = allocation_dist.idxmax()
            top_allocation_share = (allocation_dist.max() / len(df) * 100) if len(df) > 0 else 0
            
            warn_msg = "Concentration risk (>50%)" if top_allocation_share > 50 else "None"
            kpis.append(engine.build_kpi(
                category="📊 Investment Portfolio", name="Top Allocation %",
                value=f"{top_allocation} ({top_allocation_share:.2f}%)", formula="Allocation with max count", 
                source=f"`{allocation_col}`",
                warnings=warn_msg
            ))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
