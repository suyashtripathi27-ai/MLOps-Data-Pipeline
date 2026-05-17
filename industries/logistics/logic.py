import os
import pandas as pd
import numpy as np

# ==========================================
# 🧩 KPI CALCULATION MODULES
# ==========================================

def calc_sla_performance(df):
    """Calculates Time-Based and SLA KPIs if datetime columns exist."""
    report = "\n#### ⏱️ SLA & Delivery Performance\n"
    
    # Let's assume trip_creation_time and od_end_time are our proxies for total transit time
    if 'trip_creation_time' in df.columns and 'od_end_time' in df.columns:
        start = pd.to_datetime(df['trip_creation_time'], errors='coerce')
        end = pd.to_datetime(df['od_end_time'], errors='coerce')
        
        transit_time = (end - start).dt.total_seconds() / 3600 # in hours
        avg_transit = transit_time.mean()
        
        report += f"- **Average Transit Time:** {avg_transit:.2f} hours\n"
        
    if 'is_cutoff' in df.columns:
        cutoff_rate = (df['is_cutoff'].sum() / len(df)) * 100
        report += f"- **Trip Cutoff (Failure) Rate:** {cutoff_rate:.2f}%\n"
        
    return report

def calc_route_efficiency(df):
    """Calculates Route deviation and efficiency KPIs."""
    report = "\n#### 🗺️ Route Efficiency & Utilization\n"
    
    if 'actual_distance_to_destination' in df.columns and 'osrm_distance' in df.columns:
        # Calculate how much further they drove compared to the optimized (OSRM) route
        actual_dist = df['actual_distance_to_destination'].sum()
        planned_dist = df['osrm_distance'].sum()
        
        if planned_dist > 0:
            deviation = ((actual_dist - planned_dist) / planned_dist) * 100
            report += f"- **Total Route Deviation:** {deviation:.2f}% over planned OSRM distance\n"
            
    if 'factor' in df.columns:
        avg_factor = df['factor'].mean()
        report += f"- **Average Routing Factor:** {avg_factor:.2f}\n"
        
    return report

def calc_hub_intelligence(df):
    """Calculates Network and Hub bottleneck KPIs."""
    report = "\n#### 🏢 Hub & Network Intelligence\n"
    
    if 'source_name' in df.columns:
        top_sources = df['source_name'].value_counts().head(3)
        report += "- **Highest Volume Origin Hubs:**\n"
        for hub, count in top_sources.items():
            report += f"  - {hub}: {count} trips\n"
            
    return report

# ==========================================
# 🚦 THE KPI ROUTER
# ==========================================

def generate_dynamic_kpis(df):
    """
    Scans the dataframe columns and only triggers the KPI modules 
    that the dataset can support.
    """
    print("🚦 Scanning columns to determine available KPIs...")
    columns = set(df.columns)
    
    final_kpi_text = "### 📊 2. Core Operational KPIs (System Generated)\n"
    kpis_generated = False
    
    # 1. Trigger SLA KPIs?
    if {'trip_creation_time', 'od_end_time', 'is_cutoff'}.intersection(columns):
        final_kpi_text += calc_sla_performance(df)
        kpis_generated = True
        
    # 2. Trigger Route Efficiency KPIs?
    if {'actual_distance_to_destination', 'osrm_distance', 'factor'}.intersection(columns):
        final_kpi_text += calc_route_efficiency(df)
        kpis_generated = True
        
    # 3. Trigger Hub Intelligence KPIs?
    if {'source_name', 'destination_name'}.intersection(columns):
        final_kpi_text += calc_hub_intelligence(df)
        kpis_generated = True
        
    if not kpis_generated:
        final_kpi_text += "- *Standard operational data detected. Insufficient columns to generate advanced Logistics KPIs.*\n"
        
    return final_kpi_text

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================

def run_logistics_analysis(payload, client, df=None):
    """Grabs the logistics prompt, calculates KPIs dynamically, and calls the AI."""
    print("🚚 Initializing Logistics Analysis Module...")
    
    # 1. Generate KPIs dynamically based on available columns
    kpi_text = ""
    if df is not None:
        kpi_text = generate_dynamic_kpis(df)
    
    # 2. Read the strict governance prompt
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")
    
    with open(prompt_path, "r", encoding="utf-8") as file:
        raw_prompt = file.read()
        
    # 3. Inject the payload and the dynamically generated KPIs
    final_prompt = raw_prompt.format(data_payload=payload + "\n\n" + kpi_text)
    
    # 4. Call the AI
    print("🧠 Requesting Governed Strategic Insights...")
    response = client.chat.completions.create(
        model="openrouter/free", 
        messages=[
            {"role": "system", "content": "You are a pragmatic, highly experienced Operations Analytics Consultant."},
            {"role": "user", "content": final_prompt}
        ],
    )
    
    return response.choices[0].message.content
