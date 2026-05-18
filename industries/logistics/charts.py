import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd

def generate_logistics_charts(df, output_dir="data/outputs/charts/"):
    """Generates operational charts automatically based on available schema."""
    print("📈 Generating Visual Analytics...")
    os.makedirs(output_dir, exist_ok=True)
    chart_paths = []

    # --- SCENARIO 1: Last-Mile Delivery (Hub Congestion) ---
    if 'source_name' in df.columns and 'actual_time' in df.columns and 'osrm_time' in df.columns:
        df['delay_minutes'] = df['actual_time'] - df['osrm_time']
        if pd.api.types.is_timedelta64_dtype(df['delay_minutes']):
            df['delay_minutes'] = df['delay_minutes'].dt.total_seconds() / 60.0
        
        valid_delays = df[df['delay_minutes'] > 0.1]
        if not valid_delays.empty:
            bad_hubs = valid_delays.groupby('source_name')['delay_minutes'].mean().sort_values(ascending=False).head(5)
            
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="whitegrid")
            sns.barplot(x=bad_hubs.values, y=bad_hubs.index, hue=bad_hubs.index, palette="Reds_r", legend=False)
            plt.title("🚨 Top 5 Most Congested Origin Hubs", fontsize=14, fontweight='bold')
            plt.xlabel("Average Delay (Minutes)")
            plt.ylabel("Origin Hub")
            plt.tight_layout()
            
            chart_path = os.path.join(output_dir, "top_congested_hubs.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()
            chart_paths.append(chart_path)
            print(f"✅ Last-Mile Chart saved: {chart_path}")

    # --- SCENARIO 2: Heavy Fleet (Detention Time Distribution) ---
    elif 'detention_time' in df.columns:
        valid_detention = df[df['detention_time'] > 0]
        if not valid_detention.empty:
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="whitegrid")
            
            # Draw a distribution histogram
            sns.histplot(data=valid_detention, x='detention_time', bins=40, color="darkorange", kde=True)
            plt.title("⏳ Facility Detention Time Distribution", fontsize=14, fontweight='bold')
            plt.xlabel("Detention Time (Minutes)")
            plt.ylabel("Number of Trips")
            
            # Add a vertical line for the average
            avg_detention = valid_detention['detention_time'].mean()
            plt.axvline(avg_detention, color='red', linestyle='dashed', linewidth=2, label=f'Average ({avg_detention:.1f}m)')
            plt.legend()
            plt.tight_layout()
            
            chart_path = os.path.join(output_dir, "detention_distribution.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()
            chart_paths.append(chart_path)
            print(f"✅ Heavy Fleet Chart saved: {chart_path}")

    if not chart_paths:
        print("⚠️ Not enough specific columns to generate logistics charts.")
        
    return chart_paths
