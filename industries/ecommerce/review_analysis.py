"""
Product reviews, ratings, and customer sentiment metrics.
"""
import pandas as pd
from utils.kpi_engine import KPIEngine

ECOMMERCE_CONFIG = {
    "missing_data_threshold": 8,
    "score_deduction_for_warning": 12,
    "low_confidence_threshold": 35,
}

def calc_review_metrics(df, enable_debug=False):
    """Calculate review KPIs with optional execution tracing."""
    engine = KPIEngine(df, industry_config=ECOMMERCE_CONFIG)
    
    if enable_debug:
        engine.enable_tracing()
    
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    review_col, review_series = engine.get_numeric(["review_id", "review_count", "reviews"])
    rating_col, rating_series = engine.get_numeric(["rating", "review_rating", "star_rating", "score"])
    sentiment_col, sentiment_series = engine.get_numeric(["sentiment", "sentiment_score", "review_sentiment"])
    product_col, product_series = engine.get_column(["product_id", "product", "sku"])
    
    if review_col is not None:
        total_reviews = review_series.sum()
        kpis.append(engine.build_kpi("⭐ Reviews & Ratings", "Total Reviews", f"{total_reviews:,}", "Sum(Reviews)", f"`{review_col}`"))
    
    if rating_col is not None:
        avg_rating = rating_series.mean()
        median_rating = rating_series.median()
        
        kpis.append(engine.build_kpi("⭐ Reviews & Ratings", "Avg Rating", f"{avg_rating:.2f}/5.0", "Mean(Rating)", f"`{rating_col}`"))
        kpis.append(engine.build_kpi("⭐ Reviews & Ratings", "Median Rating", f"{median_rating:.2f}/5.0", "Median(Rating)", f"`{rating_col}`"))
        
        high_rated = (rating_series >= 4).sum()
        low_rated = (rating_series <= 2).sum()
        high_rate_pct = (high_rated / len(rating_series) * 100) if len(rating_series) > 0 else 0
        low_rate_pct = (low_rated / len(rating_series) * 100) if len(rating_series) > 0 else 0
        
        kpis.append(engine.build_kpi("⭐ Reviews & Ratings", "High Ratings (4-5)", f"{high_rated:,} ({high_rate_pct:.2f}%)", "Count(Rating >= 4) / Total * 100", f"`{rating_col}`"))
        
        warn_msg = "High negative sentiment" if low_rate_pct > 25 else "None"
        kpis.append(engine.build_kpi("⭐ Reviews & Ratings", "Low Ratings (1-2)", f"{low_rated:,} ({low_rate_pct:.2f}%)", "Count(Rating <= 2) / Total * 100", f"`{rating_col}`", warnings=warn_msg))
    else:
        kpis.append(engine.log_missing("⭐ Reviews & Ratings", "Ratings", "Missing numeric 'rating'."))
    
    if sentiment_col is not None:
        avg_sentiment = sentiment_series.mean()
        kpis.append(engine.build_kpi("⭐ Reviews & Ratings", "Avg Sentiment Score", f"{avg_sentiment:.2f}", "Mean(Sentiment)", f"`{sentiment_col}`"))
    
    if product_col is not None and review_col is not None:
        reviews_per_product = df.groupby(product_col)[review_col].sum().mean()
        kpis.append(engine.build_kpi("⭐ Reviews & Ratings", "Avg Reviews per Product", f"{reviews_per_product:,.0f}", "Mean(Product Reviews)", f"`{product_col}`, `{review_col}`"))
    
    if enable_debug:
        engine.print_execution_log()
    
    return kpis
