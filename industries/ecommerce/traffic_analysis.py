import pandas as pd
from .common import confidence_for, first_column, safe_kpi
from utils.validator import SemanticValidator


def calc_traffic_metrics(df):
    kpis = []
    sessions_col = first_column(df, ["sessions", "visits", "visitors", "unique_visitors", "traffic"])
    pageviews_col = first_column(df, ["page_views", "pageviews", "views"])
    bounce_col = first_column(df, ["bounce_rate", "bounce"])
    duration_col = first_column(df, ["session_duration", "avg_session_duration", "time_on_site"])
    channel_col = first_column(df, ["channel", "source", "traffic_source", "medium"])
    if not sessions_col and not pageviews_col and not bounce_col:
        return kpis

    conf, warns = confidence_for(df, [sessions_col, pageviews_col, bounce_col, duration_col, channel_col])

    if sessions_col:
        kpis.append(safe_kpi("📈 Traffic Analysis", "Traffic Volume", f"{df[sessions_col].fillna(0).sum():,.0f}", "Sum(Sessions)", f"`{sessions_col}`", conf, warns))

    if pageviews_col and sessions_col:
        depth = (df[pageviews_col].fillna(0).sum() / df[sessions_col].fillna(0).sum()) if df[sessions_col].fillna(0).sum() > 0 else 0
        kpis.append(safe_kpi("📈 Traffic Analysis", "Pages per Session", f"{depth:.2f}", "Page Views / Sessions", f"`{pageviews_col}`, `{sessions_col}`", conf, warns))

    if bounce_col:
        bounce_rate = df[bounce_col].dropna().mean()
        kpis.append(safe_kpi("📈 Traffic Analysis", "Bounce Rate", f"{bounce_rate:.2f}%", "Mean(Bounce Rate)", f"`{bounce_col}`", conf, warns))

    if duration_col:
        duration_series = df[duration_col].dropna()
        if SemanticValidator.is_valid_duration(duration_series)[0]:
            kpis.append(safe_kpi("📈 Traffic Analysis", "Avg Session Duration", f"{duration_series.mean():.2f}", "Mean(Session Duration)", f"`{duration_col}`", conf, warns))

    if channel_col:
        channel_share = df[channel_col].astype(str).value_counts(normalize=True).iloc[0] * 100 if not df[channel_col].dropna().empty else 0
        kpis.append(safe_kpi("📈 Traffic Analysis", "Top Channel Share", f"{channel_share:.2f}%", "Largest Traffic Channel / Total Traffic * 100", f"`{channel_col}`", conf, warns))

    return kpis
