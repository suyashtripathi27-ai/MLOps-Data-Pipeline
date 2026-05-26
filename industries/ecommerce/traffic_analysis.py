"""
Website traffic, sessions, and user engagement metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

# Ecommerce industry configuration
ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_traffic_metrics(df, enable_debug=False):
    """
    Calculate traffic KPIs with optional execution tracing.
    """
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    sessions_col, sessions_series = engine.get_numeric(["sessions", "visits", "page_sessions", "site_sessions"])
    users_col, users_series = engine.get_numeric(["users", "unique_users", "unique_visitors", "visitors"])
    pageviews_col, pageviews_series = engine.get_numeric(["pageviews", "page_views", "pages_viewed"])
    bounce_col, bounce_series = engine.get_numeric(["bounce_rate", "bounced_rate", "bounce_pct"])
    avg_session_col, avg_session_series = engine.get_numeric(["avg_session_duration", "avg_session_time", "session_duration"])
    source_col, source_series = engine.get_column(["traffic_source", "source", "channel"])
    
    if sessions_col is not None:
        total_sessions = sessions_series.sum()
        kpis.append(engine.build_kpi("🌐 Traffic", "Total Sessions", f"{total_sessions:,}", "Sum(Sessions)", f"`{sessions_col}`"))
    
    if users_col is not None:
        total_users = users_series.sum()
        kpis.append(engine.build_kpi("🌐 Traffic", "Total Unique Users", f"{total_users:,}", "Sum(Unique Users)", f"`{users_col}`"))
        
        if sessions_col is not None:
            total_sessions = sessions_series.sum()
            user_session_ratio = (total_sessions / total_users) if total_users > 0 else 0
            kpis.append(engine.build_kpi("🌐 Traffic", "Sessions per User", f"{user_session_ratio:.2f}", "Total Sessions / Total Users", f"`{sessions_col}`, `{users_col}`"))
    
    if pageviews_col is not None:
        total_pageviews = pageviews_series.sum()
        kpis.append(engine.build_kpi("🌐 Traffic", "Total Pageviews", f"{total_pageviews:,}", "Sum(Pageviews)", f"`{pageviews_col}`"))
        
        if sessions_col is not None:
            pages_per_session = (total_pageviews / sessions_series.sum()) if sessions_series.sum() > 0 else 0
            kpis.append(engine.build_kpi("🌐 Traffic", "Pages per Session", f"{pages_per_session:.2f}", "Total Pageviews / Sessions", f"`{pageviews_col}`, `{sessions_col}`"))
    
    if bounce_col is not None:
        avg_bounce = bounce_series.mean()
        warn_msg = "High bounce rate" if avg_bounce > 60 else "None"
        kpis.append(engine.build_kpi("🌐 Traffic", "Avg Bounce Rate", f"{avg_bounce:.2f}%", "Mean(Bounce Rate)", f"`{bounce_col}`", warnings=warn_msg))
    
    if avg_session_col is not None:
        avg_duration = avg_session_series.mean()
        kpis.append(engine.build_kpi("🌐 Traffic", "Avg Session Duration", f"{avg_duration:,.0f} sec", "Mean(Session Duration)", f"`{avg_session_col}`"))
    
    if source_col is not None:
        source_dist = source_series.value_counts().head(3)
        if len(source_dist) > 0:
            top_source = source_dist.idxmax()
            kpis.append(engine.build_kpi("🌐 Traffic", "Top Traffic Source", f"{top_source} ({source_dist.max():,} sessions)", "Source with max sessions", f"`{source_col}`"))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
