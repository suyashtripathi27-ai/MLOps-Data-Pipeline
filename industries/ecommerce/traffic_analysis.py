"""
Website traffic, sessions, and user engagement metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_traffic_metrics(df, enable_debug=False):
    kpis = []
    if len(df) == 0: return kpis
    
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    if enable_debug: engine.enable_tracing()
    
    sessions_col, sessions_series = engine.get_numeric(["sessions", "visits", "page_sessions", "site_sessions"])
    users_col, users_series = engine.get_numeric(["users", "unique_users", "unique_visitors", "visitors"])
    pageviews_col, pageviews_series = engine.get_numeric(["pageviews", "page_views", "pages_viewed"])
    bounce_col, bounce_series = engine.get_numeric(["bounce_rate", "bounced_rate", "bounce_pct"])
    avg_session_col, avg_session_series = engine.get_numeric(["avg_session_duration", "avg_session_time", "session_duration"])
    source_col, source_series = engine.get_column(["traffic_source", "source", "channel"])
    
    if sessions_col is not None:
        kpis.append(engine.build_kpi("🌐 Traffic", "Total Sessions", f"{sessions_series.sum():,}", "Sum(Sessions)", f"`{sessions_col}`"))
    else:
        kpis.append(engine.log_missing("🌐 Traffic", "Sessions", "Missing sessions data."))
        
    if users_col is not None:
        total_users = users_series.sum()
        kpis.append(engine.build_kpi("🌐 Traffic", "Total Unique Users", f"{total_users:,}", "Sum(Unique Users)", f"`{users_col}`"))
        
        if sessions_col is not None:
            user_session_ratio = (sessions_series.sum() / total_users) if total_users > 0 else 0
            kpis.append(engine.build_kpi("🌐 Traffic", "Sessions per User", f"{user_session_ratio:.2f}", "Total Sessions / Total Users", f"`{sessions_col}`, `{users_col}`"))
    else:
        kpis.append(engine.log_missing("🌐 Traffic", "Users", "Missing unique users data."))
        
    if pageviews_col is not None:
        total_pageviews = pageviews_series.sum()
        kpis.append(engine.build_kpi("🌐 Traffic", "Total Pageviews", f"{total_pageviews:,}", "Sum(Pageviews)", f"`{pageviews_col}`"))
        
        if sessions_col is not None:
            pages_per_session = (total_pageviews / sessions_series.sum()) if sessions_series.sum() > 0 else 0
            kpis.append(engine.build_kpi("🌐 Traffic", "Pages per Session", f"{pages_per_session:.2f}", "Total Pageviews / Sessions", f"`{pageviews_col}`, `{sessions_col}`"))
    else:
        kpis.append(engine.log_missing("🌐 Traffic", "Pageviews", "Missing pageviews data."))
        
    if bounce_col is not None:
        avg_bounce = bounce_series.mean()
        kpis.append(engine.build_kpi("🌐 Traffic", "Avg Bounce Rate", f"{avg_bounce:.2f}%", "Mean(Bounce Rate)", f"`{bounce_col}`", warnings="High bounce rate" if avg_bounce > 60 else "None"))
    else:
        kpis.append(engine.log_missing("🌐 Traffic", "Bounce Rate", "Missing bounce rate data."))
        
    if avg_session_col is not None:
        kpis.append(engine.build_kpi("🌐 Traffic", "Avg Session Duration", f"{avg_session_series.mean():,.0f} sec", "Mean(Session Duration)", f"`{avg_session_col}`"))
    else:
        kpis.append(engine.log_missing("🌐 Traffic", "Session Duration", "Missing duration data."))
        
    if source_col is not None:
        source_dist = source_series.value_counts().head(3)
        if len(source_dist) > 0:
            kpis.append(engine.build_kpi("🌐 Traffic", "Top Traffic Source", f"{source_dist.idxmax()} ({source_dist.max():,} sessions)", "Source with max sessions", f"`{source_col}`"))
    else:
        kpis.append(engine.log_missing("🌐 Traffic", "Traffic Source", "Missing traffic channel data."))
        
    return kpis
