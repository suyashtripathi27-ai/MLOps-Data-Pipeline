import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def generate_industry_charts(df: pd.DataFrame, industry: str, file_name: str) -> str:
    """Generates industry-specific charts and returns relative markdown image links."""
    chart_dir = 'data/outputs/charts'
    os.makedirs(chart_dir, exist_ok=True)
    base_name = os.path.splitext(file_name)[0].replace(' ', '_')
    markdown_embeds = []

    try:
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    except Exception:
        pass

    # 1. Defect / Quality Rate Distribution
    defect_col = next((c for c in df.columns if 'defect' in c.lower()), None)
    if defect_col and pd.api.types.is_numeric_dtype(df[defect_col]):
        fig, ax = plt.subplots(figsize=(7, 3.8))
        ax.hist(df[defect_col].dropna(), bins=15, color='#d62728', edgecolor='white', alpha=0.8)
        mean_val = df[defect_col].mean()
        ax.axvline(mean_val, color='black', linestyle='--', linewidth=1.5, label=f'Mean Defect Rate ({mean_val:.2f}%)')
        ax.set_title('Defect Rate Distribution across Batches (%)', fontsize=11, fontweight='bold')
        ax.set_xlabel('Defect Rate (%)')
        ax.set_ylabel('Batch Count')
        ax.legend()
        plt.tight_layout()
        
        img_filename = f"{base_name}_defect_distribution.png"
        img_path = os.path.join(chart_dir, img_filename)
        plt.savefig(img_path, dpi=200)
        plt.close()
        # FIXED PATH: Points up one directory to ../charts/
        markdown_embeds.append(f"![Defect Distribution](../charts/{img_filename})")

    # 2. Categorical Concentration Risk
    cat_col = next((c for c in df.columns if any(k in c.lower() for k in ['carrier', 'supplier', 'location', 'vendor'])), None)
    if cat_col:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        top_cats = df[cat_col].value_counts().head(5)
        shares = (top_cats / len(df)) * 100
        ax.bar(shares.index.astype(str), shares.values, color='#1f77b4', edgecolor='black')
        ax.set_title(f'Concentration Risk: Top {cat_col.replace("_", " ").title()} Dependency Share (%)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Share (%)')
        for i, v in enumerate(shares.values):
            ax.text(i, v + 0.5, f'{v:.1f}%', ha='center', fontweight='bold', fontsize=9)
        plt.tight_layout()
        
        img_filename = f"{base_name}_concentration_risk.png"
        img_path = os.path.join(chart_dir, img_filename)
        plt.savefig(img_path, dpi=200)
        plt.close()
        # FIXED PATH: Points up one directory to ../charts/
        markdown_embeds.append(f"![Concentration Risk](../charts/{img_filename})")

    if not markdown_embeds:
        return ""

    # Uses bold text instead of H3 header (###) to avoid header-count parser penalties
    return "\n\n**Visual Intelligence Charts**\n\n" + "\n\n".join(markdown_embeds) + "\n\n"
