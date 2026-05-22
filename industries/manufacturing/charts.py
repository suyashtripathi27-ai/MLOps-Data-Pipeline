import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def _first_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def generate_manufacturing_charts(df, output_dir="data/outputs/charts/"):
    """Generates manufacturing charts based on available schema."""
    print("📈 Generating Manufacturing Visual Analytics...")
    os.makedirs(output_dir, exist_ok=True)
    chart_paths = []

    date_col = _first_column(df, ["date", "production_date", "timestamp", "shift_date"])
    units_col = _first_column(df, ["units_produced", "production_quantity", "output_qty", "good_units"])

    if date_col and units_col:
        trend_df = pd.DataFrame(
            {
                "date": pd.to_datetime(df[date_col], errors="coerce"),
                "units": df[units_col],
            }
        ).dropna()
        if not trend_df.empty:
            daily = trend_df.groupby(trend_df["date"].dt.date)["units"].sum().reset_index()
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="whitegrid")
            sns.lineplot(data=daily, x="date", y="units", marker="o", color="steelblue")
            plt.title("🏭 Daily Production Trend", fontsize=14, fontweight="bold")
            plt.xlabel("Date")
            plt.ylabel("Units Produced")
            plt.xticks(rotation=45)
            plt.tight_layout()
            chart_path = os.path.join(output_dir, "manufacturing_daily_output_trend.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()
            chart_paths.append(chart_path)
            print(f"✅ Chart saved: {chart_path}")

    machine_col = _first_column(df, ["machine_id", "line_id", "workcenter"])
    defect_col = _first_column(df, ["defect_count", "defective_units", "reject_units"])

    if machine_col and defect_col:
        defects = (
            df[[machine_col, defect_col]]
            .dropna()
            .groupby(machine_col)[defect_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        if not defects.empty:
            plt.figure(figsize=(10, 6))
            sns.set_theme(style="whitegrid")
            sns.barplot(x=defects.values, y=defects.index, hue=defects.index, palette="Reds_r", legend=False)
            plt.title("🚨 Top 10 Lines/Machines by Defects", fontsize=14, fontweight="bold")
            plt.xlabel("Total Defects")
            plt.ylabel("Line / Machine")
            plt.tight_layout()
            chart_path = os.path.join(output_dir, "manufacturing_top_defect_sources.png")
            plt.savefig(chart_path, dpi=300)
            plt.close()
            chart_paths.append(chart_path)
            print(f"✅ Chart saved: {chart_path}")

    if not chart_paths:
        print("⚠️ Not enough specific columns to generate manufacturing charts.")

    return chart_paths
