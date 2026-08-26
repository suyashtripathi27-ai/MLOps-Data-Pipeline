import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def _is_id_like(series: pd.Series, total_rows: int) -> bool:
    """
    True if a numeric column is almost certainly an identifier/index rather
    than a business metric -- e.g. RowNumber, CustomerId, a mis-mapped
    shipment_id. IDs are virtually always ~unique per row; a real business
    metric (revenue, balance, credit score) repeats values constantly.
    Doesn't rely on column naming, since that's exactly what breaks on
    schema-mapping mismatches (a real fallback needs to survive those, not
    assume they never happen).
    """
    if total_rows == 0:
        return False
    return series.nunique(dropna=True) / total_rows > 0.95


def _is_high_cardinality_noise(series: pd.Series, total_rows: int) -> bool:
    """
    True if a categorical column is too fragmented to produce a meaningful
    'top 5 share' chart -- e.g. Surname, free-text notes, an ID stored as a
    string. A real business category (Country, Department, Product) repeats
    heavily across rows; each value in a noise column barely repeats at all.
    """
    if total_rows == 0:
        return False
    return series.nunique(dropna=True) / total_rows > 0.5


def generate_industry_charts(df: pd.DataFrame, industry: str, file_name: str) -> str:
    """Generates universal charts for any dataset and returns root-relative markdown links."""
    chart_dir = 'data/outputs/charts'
    os.makedirs(chart_dir, exist_ok=True)
    base_name = os.path.splitext(file_name)[0].replace(' ', '_').replace('(', '').replace(')', '')
    markdown_embeds = []
    total_rows = len(df)

    try:
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    except Exception:
        pass

    # 1. PRIMARY NUMERIC DISTRIBUTION CHART (Revenue, Units, Cost, or Primary Metric)
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    # Prioritize key business metrics
    priority_num = next((c for c in num_cols if any(k in c.lower() for k in ['revenue', 'amount', 'boxes', 'quantity', 'cost', 'sales', 'defect'])), None)
    # Fallback: first numeric column that ISN'T an ID/index -- prevents charting
    # "Distribution" of a row number or customer ID just because it happened
    # to be the first numeric column in the dataframe.
    fallback_num = next((c for c in num_cols if not _is_id_like(df[c], total_rows)), None)
    target_num = priority_num or fallback_num

    if target_num:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        clean_data = df[target_num].dropna()
        ax.hist(clean_data, bins=15, color='#1f77b4', edgecolor='white', alpha=0.85)
        mean_val = clean_data.mean()
        ax.axvline(mean_val, color='#d62728', linestyle='--', linewidth=1.5, label=f'Mean: {mean_val:,.2f}')
        ax.set_title(f'{target_num.replace("_", " ").title()} Distribution', fontsize=11, fontweight='bold')
        ax.set_xlabel(target_num.replace('_', ' ').title())
        ax.set_ylabel('Record Frequency')
        ax.legend()
        plt.tight_layout()
        
        img_filename = f"{base_name}_{target_num.lower().replace(' ', '_')}_dist.png"
        img_path = os.path.join(chart_dir, img_filename)
        plt.savefig(img_path, dpi=200)
        plt.close()
        markdown_embeds.append(f"![{target_num} Distribution](/data/outputs/charts/{img_filename})")

    # 2. TOP CATEGORICAL SHARE / CONCENTRATION CHART (Product, Country, Sales Rep, Category)
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    priority_cat = next((c for c in cat_cols if any(k in c.lower() for k in ['product', 'country', 'sales', 'carrier', 'supplier', 'location', 'category', 'department'])), None)
    # Fallback: among non-noise categorical columns (not near-unique-per-row,
    # like Surname or free text), pick the LOWEST-cardinality one -- the more
    # a value repeats, the more likely it's a real business category rather
    # than incidental per-row text.
    candidate_cats = [c for c in cat_cols if not _is_high_cardinality_noise(df[c], total_rows)]
    fallback_cat = min(candidate_cats, key=lambda c: df[c].nunique(dropna=True)) if candidate_cats else None
    target_cat = priority_cat or fallback_cat

    if target_cat:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        top_counts = df[target_cat].value_counts().head(5)
        shares = (top_counts / len(df)) * 100
        ax.bar(top_counts.index.astype(str), shares.values, color='#2ca02c', edgecolor='black', alpha=0.85)
        ax.set_title(f'Top 5 {target_cat.replace("_", " ").title()} Volume Share (%)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Share (%)')
        for i, v in enumerate(shares.values):
            ax.text(i, v + 0.5, f'{v:.1f}%', ha='center', fontweight='bold', fontsize=9)
        plt.tight_layout()
        
        img_filename = f"{base_name}_{target_cat.lower().replace(' ', '_')}_share.png"
        img_path = os.path.join(chart_dir, img_filename)
        plt.savefig(img_path, dpi=200)
        plt.close()
        markdown_embeds.append(f"![{target_cat} Share](/data/outputs/charts/{img_filename})")

    # 3. TREND OVER TIME (new chart type) -- when a date column and a real
    # business metric both exist, a trend line adds a dimension neither of
    # the two charts above can show: direction and volatility over time,
    # not just a snapshot distribution.
    date_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns.tolist()
    if not date_cols:
        for c in df.columns:
            if 'date' in c.lower() and c not in df.select_dtypes(include=['number']).columns:
                try:
                    pd.to_datetime(df[c].dropna().head(20))
                    date_cols.append(c)
                    break
                except Exception:
                    continue

    if date_cols and target_num:
        try:
            date_col = date_cols[0]
            trend_df = df[[date_col, target_num]].dropna().copy()
            trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors='coerce')
            trend_df = trend_df.dropna(subset=[date_col]).sort_values(date_col)

            if len(trend_df) >= 5 and trend_df[date_col].nunique() >= 3:
                trend_series = trend_df.set_index(date_col)[target_num].resample('D').mean().dropna()
                # Too sparse daily -- fall back to monthly aggregation instead
                if len(trend_series) < 5:
                    trend_series = trend_df.set_index(date_col)[target_num].resample('ME').mean().dropna()

                if len(trend_series) >= 3:
                    fig, ax = plt.subplots(figsize=(7, 3.8))
                    ax.plot(trend_series.index, trend_series.values, color='#ff7f0e', linewidth=2, marker='o', markersize=3)
                    ax.set_title(f'{target_num.replace("_", " ").title()} Trend Over Time', fontsize=11, fontweight='bold')
                    ax.set_ylabel(target_num.replace('_', ' ').title())
                    ax.set_xlabel(date_col.replace('_', ' ').title())
                    plt.xticks(rotation=30, ha='right')
                    plt.tight_layout()

                    img_filename = f"{base_name}_{target_num.lower().replace(' ', '_')}_trend.png"
                    img_path = os.path.join(chart_dir, img_filename)
                    plt.savefig(img_path, dpi=200)
                    plt.close()
                    markdown_embeds.append(f"![{target_num} Trend](/data/outputs/charts/{img_filename})")
        except Exception:
            pass  # Trend chart is additive -- never let it break the other two

    if not markdown_embeds:
        return ""

    return "\n\n**Visual Intelligence Charts**\n\n" + "\n\n".join(markdown_embeds) + "\n\n"
