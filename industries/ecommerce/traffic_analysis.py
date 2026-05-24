"""
Website traffic, sessions, and user engagement metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_traffic_metrics(df):
    """Calculates traffic and engagement KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    sessions_col = first_column(df, ["sessions", "visits", "page_sessions", "site_sessions"])
    users_col = first_column(df, ["users", "unique_users", "unique_visitors", "visitors"])
    pageviews_col = first_column(df, ["pageviews", "page_views", "pages_viewed"])
    bounce_col = first_column(df, ["bounce_rate", "bounced_rate", "bounce_pct"])
    avg_session_col = first_column(df, ["avg_session_duration", "avg_session_time", "session_duration"])
    source_col = first_column(df, ["traffic_source", "source", "channel"])
    
    if not sessions_col and not users_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [sessions_col, users_col, pageviews_col, bounce_col, avg_session_col, source_col] if col])
    
    # Sessions
    if sessions_col and pd.api.types.is_numeric_dtype(df[sessions_col]):
        total_sessions = df[sessions_col].sum()
        
        kpis.append(safe_kpi(
            category="🌐 Traffic",
            name="Total Sessions",
            value=f"{total_sessions:,}",
            formula="Sum(Sessions)",
            source=f"`{sessions_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Users
    if users_col and pd.api.types.is_numeric_dtype(df[users_col]):
        total_users = df[users_col].sum()
        
        kpis.append(safe_kpi(
            category="🌐 Traffic",
            name="Total Unique Users",
            value=f"{total_users:,}",
            formula="Sum(Unique Users)",
            source=f"`{users_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # User to session ratio
        if sessions_col and pd.api.types.is_numeric_dtype(df[sessions_col]):
            total_sessions = df[sessions_col].sum()
            user_session_ratio = (total_sessions / total_users) if total_users > 0 else 0
            
            kpis.append(safe_kpi(
                category="🌐 Traffic",
                name="Sessions per User",
                value=f"{user_session_ratio:.2f}",
                formula="Total Sessions / Total Users",
                source=f"`{sessions_col}`, `{users_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Pageviews
    if pageviews_col and pd.api.types.is_numeric_dtype(df[pageviews_col]):
        total_pageviews = df[pageviews_col].sum()
        
        kpis.append(safe_kpi(
            category="🌐 Traffic",
            name="Total Pageviews",
            value=f"{total_pageviews:,}",
            formula="Sum(Pageviews)",
            source=f"`{pageviews_col}`",
            confidence=conf,
            warnings=warns
        ))
        
        # Pages per session
        if sessions_col and pd.api.types.is_numeric_dtype(df[sessions_col]):
            pages_per_session = (total_pageviews / df[sessions_col].sum()) if df[sessions_col].sum() > 0 else 0
            
            kpis.append(safe_kpi(
                category="🌐 Traffic",
                name="Pages per Session",
                value=f"{pages_per_session:.2f}",
                formula="Total Pageviews / Sessions",
                source=f"`{pageviews_col}`, `{sessions_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Bounce rate
    if bounce_col and pd.api.types.is_numeric_dtype(df[bounce_col]):
        valid_bounce = df[bounce_col].dropna()
        
        if not valid_bounce.empty:
            avg_bounce = valid_bounce.mean()
            
            kpis.append(safe_kpi(
                category="🌐 Traffic",
                name="Avg Bounce Rate",
                value=f"{avg_bounce:.2f}%",
                formula="Mean(Bounce Rate)",
                source=f"`{bounce_col}`",
                confidence=conf,
                warnings="High bounce rate" if avg_bounce > 60 else warns
            ))
    
    # Session duration
    if avg_session_col and pd.api.types.is_numeric_dtype(df[avg_session_col]):
        valid_duration = df[avg_session_col].dropna()
        
        if not valid_duration.empty:
            avg_duration = valid_duration.mean()
            
            kpis.append(safe_kpi(
                category="🌐 Traffic",
                name="Avg Session Duration",
                value=f"{avg_duration:,.0f} sec",
                formula="Mean(Session Duration)",
                source=f"`{avg_session_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Traffic by source
    if source_col:
        source_dist = df[source_col].value_counts().head(3)
        
        if not source_dist.empty:
            top_source = source_dist.idxmax()
            
            kpis.append(safe_kpi(
                category="🌐 Traffic",
                name="Top Traffic Source",
                value=f"{top_source} ({source_dist.max():,} sessions)",
                formula="Source with max sessions",
                source=f"`{source_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    return kpis
