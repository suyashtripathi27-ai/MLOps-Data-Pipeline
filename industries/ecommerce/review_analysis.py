"""
Product reviews, ratings, and customer sentiment metrics.
"""
import pandas as pd
from utils.kpi_helpers import first_column, safe_kpi, confidence_for

def calc_review_metrics(df):
    """Calculates review and sentiment KPIs."""
    kpis = []
    
    if len(df) == 0:
        return kpis
    
    review_col = first_column(df, ["review_id", "review_count", "reviews"])
    rating_col = first_column(df, ["rating", "review_rating", "star_rating", "score"])
    sentiment_col = first_column(df, ["sentiment", "sentiment_score", "review_sentiment"])
    product_col = first_column(df, ["product_id", "product", "sku"])
    
    if not rating_col and not review_col:
        return kpis
    
    conf, warns = confidence_for(df, [col for col in [review_col, rating_col, sentiment_col, product_col] if col])
    
    # Total reviews
    if review_col and pd.api.types.is_numeric_dtype(df[review_col]):
        total_reviews = df[review_col].sum()
        
        kpis.append(safe_kpi(
            category="⭐ Reviews & Ratings",
            name="Total Reviews",
            value=f"{total_reviews:,}",
            formula="Sum(Reviews)",
            source=f"`{review_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    # Rating metrics
    if rating_col and pd.api.types.is_numeric_dtype(df[rating_col]):
        valid_ratings = df[rating_col].dropna()
        
        if not valid_ratings.empty:
            avg_rating = valid_ratings.mean()
            median_rating = valid_ratings.median()
            
            kpis.append(safe_kpi(
                category="⭐ Reviews & Ratings",
                name="Avg Rating",
                value=f"{avg_rating:.2f}/5.0",
                formula="Mean(Rating)",
                source=f"`{rating_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="⭐ Reviews & Ratings",
                name="Median Rating",
                value=f"{median_rating:.2f}/5.0",
                formula="Median(Rating)",
                source=f"`{rating_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            # Rating distribution
            high_rated = (valid_ratings >= 4).sum()
            low_rated = (valid_ratings <= 2).sum()
            high_rate_pct = (high_rated / len(valid_ratings) * 100) if len(valid_ratings) > 0 else 0
            low_rate_pct = (low_rated / len(valid_ratings) * 100) if len(valid_ratings) > 0 else 0
            
            kpis.append(safe_kpi(
                category="⭐ Reviews & Ratings",
                name="High Ratings (4-5)",
                value=f"{high_rated:,} ({high_rate_pct:.2f}%)",
                formula="Count(Rating >= 4) / Total * 100",
                source=f"`{rating_col}`",
                confidence=conf,
                warnings=warns
            ))
            
            kpis.append(safe_kpi(
                category="⭐ Reviews & Ratings",
                name="Low Ratings (1-2)",
                value=f"{low_rated:,} ({low_rate_pct:.2f}%)",
                formula="Count(Rating <= 2) / Total * 100",
                source=f"`{rating_col}`",
                confidence=conf,
                warnings="High negative sentiment" if low_rate_pct > 25 else warns
            ))
    
    # Sentiment analysis
    if sentiment_col and pd.api.types.is_numeric_dtype(df[sentiment_col]):
        valid_sentiment = df[sentiment_col].dropna()
        
        if not valid_sentiment.empty:
            avg_sentiment = valid_sentiment.mean()
            
            kpis.append(safe_kpi(
                category="⭐ Reviews & Ratings",
                name="Avg Sentiment Score",
                value=f"{avg_sentiment:.2f}",
                formula="Mean(Sentiment)",
                source=f"`{sentiment_col}`",
                confidence=conf,
                warnings=warns
            ))
    
    # Reviews per product
    if product_col and review_col:
        reviews_per_product = df.groupby(product_col)[review_col].sum().mean()
        
        kpis.append(safe_kpi(
            category="⭐ Reviews & Ratings",
            name="Avg Reviews per Product",
            value=f"{reviews_per_product:,.0f}",
            formula="Mean(Product Reviews)",
            source=f"`{product_col}`, `{review_col}`",
            confidence=conf,
            warnings=warns
        ))
    
    return kpis
