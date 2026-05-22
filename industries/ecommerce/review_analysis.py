import pandas as pd
from .common import confidence_for, first_column, safe_kpi
from utils.validator import SemanticValidator


def calc_review_metrics(df):
    kpis = []
    rating_col = first_column(df, ["rating", "review_rating", "score", "stars"])
    review_col = first_column(df, ["review_text", "review", "comment", "feedback"])
    review_count_col = first_column(df, ["review_count", "reviews", "num_reviews"])
    if not rating_col and not review_count_col and not review_col:
        return kpis

    conf, warns = confidence_for(df, [rating_col, review_count_col, review_col])

    if rating_col:
        ratings = df[rating_col].dropna()
        if not ratings.empty:
            kpis.append(safe_kpi("⭐ Review Analysis", "Avg Rating", f"{ratings.mean():.2f}", "Mean(Rating)", f"`{rating_col}`", conf, warns))
            kpis.append(safe_kpi("⭐ Review Analysis", "Low Rating Rate", f"{(ratings <= 2).mean() * 100:.2f}%", "Ratings <= 2 / Total Ratings * 100", f"`{rating_col}`", conf, warns))
            kpis.append(safe_kpi("⭐ Review Analysis", "Rating Volatility", f"{ratings.std(ddof=0):.2f}", "StdDev(Rating)", f"`{rating_col}`", conf, warns))

    if review_count_col:
        kpis.append(safe_kpi("⭐ Review Analysis", "Review Volume", f"{df[review_count_col].fillna(0).sum():,.0f}", "Sum(Review Count)", f"`{review_count_col}`", conf, warns))

    if review_col:
        non_empty = df[review_col].astype(str).str.strip().ne("")
        kpis.append(safe_kpi("⭐ Review Analysis", "Text Review Coverage", f"{non_empty.mean() * 100:.2f}%", "Non-empty Reviews / Total Rows * 100", f"`{review_col}`", conf, warns))

    return kpis
