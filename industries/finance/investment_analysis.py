"""
Investment performance, returns, and portfolio metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_investment_metrics(df):
    """Calculates investment performance KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    portfolio_value_col = first_column(df, ["portfolio_value", "total_value", "market_value"])
    return_col = first_column(df, ["return", "investment_return", "roi", "return_pct"])
    invested_col = first_column(df, ["amount_invested", "principal", "capital_invested"])
    gain_col = first_column(df, ["gain", "investment_gain", "profit"])
    asset_class_col = first_column(df, ["asset_class", "security_type", "investment_type"])
    
    if not portfolio_value_col and not return_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [portfolio_value_col, return_col, invested_col, gain_col, asset_class_col] if col])
    
    # Portfolio value
    if portfolio_value_col and pd.api.types.is_numeric_dtype(df[portfolio_value_col]):
        total_portfolio = df[portfolio_value_col].sum()
        
        kpis.append(safe_kpi(
            category="💼 Investment",
            name="Total Portfolio Value",
            value=f"${total_portfolio:,.2f}",
            formula="Sum(Portfolio Value)",
            source=f"`{portfolio_value_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Returns
    if return_col and pd.api.types.is_numeric_dtype(df[return_col]):
        valid_return = df[return_col].dropna()
        
        if not valid_return.empty:
            avg_return = valid_return.mean()
            
            kpis.append(safe_kpi(
                category="💼 Investment",
                name="Average Return",
                value=f"{avg_return:.2f}%",
                formula="Mean(Return %)",
                source=f"`{return_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            # Positive vs negative returns
            positive_return = (valid_return > 0).sum()
            negative_return = (valid_return < 0).sum()
            positive_pct = (positive_return / len(valid_return) * 100) if len(valid_return) > 0 else 0
            
            kpis.append(safe_kpi(
                category="💼 Investment",
                name="Win Rate (Positive Returns)",
                value=f"{positive_pct:.2f}%",
                formula="(Positions with +Return / Total) * 100",
                source=f"`{return_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Gains
    if gain_col and pd.api.types.is_numeric_dtype(df[gain_col]):
        total_gain = df[gain_col].sum()
        
        kpis.append(safe_kpi(
            category="💼 Investment",
            name="Total Investment Gain",
            value=f"${total_gain:,.2f}",
            formula="Sum(Gain)",
            source=f"`{gain_col}`",
            confidence=conf,
            warnings="Net loss" if total_gain < 0 else warns
        ))
    
    # ROI calculation
    if invested_col and gain_col and pd.api.types.is_numeric_dtype(df[invested_col]) and pd.api.types.is_numeric_dtype(df[gain_col]):
        total_invested = df[invested_col].sum()
        total_gain = df[gain_col].sum()
        
        roi = (total_gain / total_invested * 100) if total_invested > 0 else 0
        
        kpis.append(safe_kpi(
            category="💼 Investment",
            name="Return on Investment (ROI)",
            value=f"{roi:.2f}%",
            formula="(Total Gain / Total Invested) * 100",
            source=f"`{gain_col}`, `{invested_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Asset class breakdown
    if asset_class_col:
        asset_values = df.groupby(asset_class_col)[portfolio_value_col].sum().sort_values(ascending=False) if portfolio_value_col else None
        
        if asset_values is not None and not asset_values.empty:
            total_val = asset_values.sum()
            top_class = asset_values.idxmax()
            top_class_val = asset_values.max()
            top_class_pct = (top_class_val / total_val * 100) if total_val > 0 else 0
            
            kpis.append(safe_kpi(
                category="💼 Investment",
                name="Top Asset Class",
                value=f"{top_class} (${top_class_val:,.2f})",
                formula="Asset class with max value",
                source=f"`{asset_class_col}`, `{portfolio_value_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="💼 Investment",
                name="Top Asset Concentration",
                value=f"{top_class_pct:.2f}%",
                formula="(Top Class / Total) * 100",
                source=f"`{asset_class_col}`, `{portfolio_value_col}`",
                confidence=conf,
                warnings="High concentration" if top_class_pct > 40 else warns
            ))
    
    return kpis
