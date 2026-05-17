import os
import pandas as pd

def calculate_logistics_kpis(df):
    """
    BUSINESS INTELLIGENCE: Calculates logistics-specific metrics.
    It checks if the required columns exist, and if so, calculates the KPIs.
    """
    kpi_report = "### 📈 Logistics KPIs Detected\n"
    kpi_found = False

    # Example 1: SLA Breach Calculation
    # If the dataset has 'actual_delivery_time' and 'expected_delivery_time'
    if 'actual_delivery_time' in df.columns and 'expected_delivery_time' in df.columns:
        # Convert to datetime just in case
        actual = pd.to_datetime(df['actual_delivery_time'], errors='coerce')
        expected = pd.to_datetime(df['expected_delivery_time'], errors='coerce')
        
        late_deliveries = (actual > expected).sum()
        total_deliveries = len(df)
        breach_rate = (late_deliveries / total_deliveries) * 100
        
        kpi_report += f"* **SLA Breach Rate:** {breach_rate:.2f}% ({late_deliveries} late shipments)\n"
        kpi_found = True

    # Example 2: Route Cost / Distance Efficiency
    if 'trip_distance' in df.columns or 'osrm_distance' in df.columns:
        dist_col = 'trip_distance' if 'trip_distance' in df.columns else 'osrm_distance'
        avg_dist = df[dist_col].mean()
        max_dist = df[dist_col].max()
        kpi_report += f"* **Average Trip Distance:** {avg_dist:.2f} units (Max: {max_dist:.2f})\n"
        kpi_found = True

    # If no specific logistics columns were found, just return a generic message
    if not kpi_found:
        kpi_report += "* Standard operational data detected without strict SLA columns.\n"

    return kpi_report


def run_logistics_analysis(payload, client, df=None):
    """
    Grabs the logistics prompt, calculates KPIs, injects the payload, and calls the AI.
    """
    print("🚚 Initializing Logistics Analysis Module...")
    
    # 1. Calculate Business KPIs (if dataframe is passed)
    kpi_text = ""
    if df is not None:
        kpi_text = calculate_logistics_kpis(df)
    
    # 2. Read the text prompt from the SAME folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")
    
    with open(prompt_path, "r", encoding="utf-8") as file:
        raw_prompt = file.read()
        
    # 3. Inject BOTH the math payload and the custom KPIs into the prompt
    final_prompt = raw_prompt.format(data_payload=payload + "\n\n" + kpi_text)
    
    # 4. Call the AI
    print("🧠 Requesting Strategic Route Optimization Insights...")
    response = client.chat.completions.create(
        model="openrouter/free", 
        messages=[
            {"role": "system", "content": "You are an elite supply chain consultant."},
            {"role": "user", "content": final_prompt}
        ],
    )
    
    return response.choices[0].message.content
