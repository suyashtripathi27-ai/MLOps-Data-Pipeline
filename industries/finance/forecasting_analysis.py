"""
Revenue, growth, and ticket value metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for
from utils.validator import SemanticValidator

def calc_revenue_metrics(df):
    """Calculates revenue and growth KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    revenue_col = first_column(df, ["revenue", "sales", "turnover", "gross_revenue"])
    date_col = first_column(df, ["date", "period", "transaction_date", "reporting_date"])
    ticket_col = first_column(df, ["avg_ticket", "ticket_value", "amount", "transaction_value"])
    segment_col = first_column(df, ["segment", "business_unit", "revenue_source", "product_line"])
    
    if not revenue_col:
        return kpis
    
    # Revenue is MONEY, not duration
    if not pd.api.types.is_numeric_dtype(df[revenue_col]):
        kpis.append(safe_kpi(
            category="📈 Revenue",
            name="Revenue Metrics",
            value="EXCLUDED",
            formula="N/A",
            source=f"`{revenue_col}`",
            confidence="Low",
            warnings="Revenue column contains non-numeric data."
        ))
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [revenue_col, date_col, ticket_col, segment_col] if col])
    
    # Total revenue
    total_revenue = df[revenue_col].sum()
    avg_revenue = df[revenue_col].mean()
    
    kpis.append(safe_kpi(
        category="📈 Revenue",
        name="Total Revenue",
        value=f"${total_revenue:,.2f}",
        formula="Sum(Revenue)",
        source=f"`{revenue_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    kpis.append(safe_kpi(
        category="📈 Revenue",
        name="Average Revenue (per Period/Record)",
        value=f"${avg_revenue:,.2f}",
        formula="Mean(Revenue)",
        source=f"`{revenue_col}`",
        confidence=conf,
        warnings=warns
    ))
    
    # Ticket metrics
    if ticket_col and pd.api.types.is_numeric_dtype(df[ticket_col]):
        valid_ticket = df[ticket_col].dropna()
        
        if not valid_ticket.empty:
            avg_ticket = valid_ticket.mean()
            max_ticket = valid_ticket.max()
            
            kpis.append(safe_kpi(
                category="📈 Revenue",
                name="Avg Ticket Value",
                value=f"${avg_ticket:,.2f}",
                formula="Mean(Ticket Value)",
                source=f"`{ticket_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="📈 Revenue",
                name="Max Ticket Value",
                value=f"${max_ticket:,.2f}",
                formula="Max(Ticket Value)",
                source=f"`{ticket_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Revenue by segment
    if segment_col:
        segment_revenue = df.groupby(segment_col)[revenue_col].sum().sort_values(ascending=False)
        
        if not segment_revenue.empty:
            top_segment = segment_revenue.idxmax()
            top_segment_revenue = segment_revenue.max()
            top_segment_share = (top_segment_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            kpis.append(safe_kpi(
                category="📈 Revenue",
                name="Top Revenue Segment",
                value=f"{top_segment} (${top_segment_revenue:,.2f})",
                formula="Segment with max revenue",
                source=f"`{segment_col}`, `{revenue_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="📈 Revenue",
                name="Top Segment Revenue Share",
                value=f"{top_segment_share:.2f}%",
                formula="Top Segment / Total Revenue * 100",
                source=f"`{segment_col}`, `{revenue_col}`",
                confidence=conf,
                warnings="High concentration" if top_segment_share > 40 else warns
            ))
    
    # Growth metrics (if date exists)
    if date_col:
        date_df = df.copy()
        date_df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
        date_df = date_df.dropna(subset=["_date"])
        
        if not date_df.empty:
            # Check if date is valid
            dt_valid, _ = SemanticValidator.is_valid_datetime(date_df["_date"])
            
            if dt_valid:
                try:
                    date_df_indexed = date_df.set_index("_date")
                    monthly_revenue = date_df_indexed[revenue_col].resample('ME').sum()
                    
                    if len(monthly_revenue) >= 2:
                        first_month = monthly_revenue.iloc[0]
                        last_month = monthly_revenue.iloc[-1]
                        growth = ((last_month - first_month) / first_month * 100) if first_month > 0 else 0
                        
                        kpis.append(safe_kpi(
                            category="📈 Revenue",
                            name="Revenue Growth %",
                            value=f"{growth:.2f}%",
                            formula="((Last Month - First Month) / First Month) * 100",
                            source=f"`{revenue_col}`, `{date_col}`",
                            confidence=conf,
                            warnings=warns
                        ))
                        
                        avg_monthly_growth = monthly_revenue.pct_change().dropna().mean() * 100
                        
                        kpis.append(safe_kpi(
                            category="📈 Revenue",
                            name="Avg Monthly Growth Rate",
                            value=f"{avg_monthly_growth:.2f}%",
                            formula="Mean(Monthly % Change)",
                            source=f"`{revenue_col}`, `{date_col}`",
                            confidence=conf,
                            warnings=warns
                        ))
                except Exception:
                    pass
    
    return kpis
