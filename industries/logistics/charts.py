import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_logistics_charts(df, output_dir="data/outputs/charts/"):
    """
    Generates operational charts and saves them as PNG files.
    """
    print("📈 Generating Visual Analytics...")
    os.makedirs(output_dir, exist_ok=True)
    chart_paths = []

    # Example 1: Top 5 Most Congested Hubs (Bar Chart)
    if 'source_name' in df.columns and 'actual_time' in df.columns and 'osrm_time' in df.columns:
        # Calculate delay
        df['delay_minutes'] = df['actual_time'] - df['osrm_time']
        
        # Group by hub and get the top 5 worst offenders
        bad_hubs = df[df['delay_minutes'] > 0].groupby('source_name')['delay_minutes'].mean().sort_values(ascending=False).head(5)
        
        if not bad_hubs.empty:
            # Set up the plot style
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="whitegrid")
            
            # Draw a red bar chart to indicate delays
            sns.barplot(x=bad_hubs.values, y=bad_hubs.index, hue=bad_hubs.index, palette="Reds_r", legend=False)
            
            # Add labels and title
            plt.title("🚨 Top 5 Most Congested Origin Hubs (Avg Delay in Minutes)", fontsize=14, fontweight='bold')
            plt.xlabel("Average Delay (Minutes)", fontsize=12)
            plt.ylabel("Origin Hub", fontsize=12)
            plt.tight_layout()
            
            # Save the image
            chart_path = os.path.join(output_dir, "top_congested_hubs.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()
            
            print(f"✅ Chart successfully saved to: {chart_path}")
            chart_paths.append(chart_path)

    if not chart_paths:
        print("⚠️ Not enough data to generate logistics charts.")
        
    return chart_paths
