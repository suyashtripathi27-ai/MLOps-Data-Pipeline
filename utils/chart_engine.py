import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def generate_industry_charts(df: pd.DataFrame, industry: str, file_name: str) -> str:
    """Generates universal charts for any dataset and returns root-relative markdown links."""
    chart_dir = 'data/outputs/charts'
    os.makedirs(chart_dir, exist_ok=True)
    base_name = os.path.splitext(file_name)[0].replace(' ', '_').replace('(', '').replace(')', '')
    markdown_embeds = []

    try:
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    except Exception:
        pass

    # 1. PRIMARY NUMERIC DISTRIBUTION CHART (Revenue, Units, Cost, or Primary Metric)
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    # Prioritize key business metrics
    priority_num = next((c for c in num_cols if any(k in c.lower() for k in ['revenue', 'amount', 'boxes', 'quantity', 'cost', 'sales', 'defect'])), None)
    target_num = priority_num or (num_cols[0] if num_cols else None)

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
    target_cat = priority_cat or (cat_cols[0] if cat_cols else None)

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

    if not markdown_embeds:
        return ""

    return "\n\n**Visual Intelligence Charts**\n\n" + "\n\n".join(markdown_embeds) + "\n\n"
