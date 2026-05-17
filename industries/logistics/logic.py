import os
import pandas as pd

# ==========================================
# 🧩 TRACEABLE KPI CALCULATION MODULES
# ==========================================

def calc_sla_performance(df):
    """Calculates Time-Based and SLA KPIs with full traceability."""
    report = "\n#### ⏱️ SLA & Delivery Performance KPIs\n"
    
    if 'trip_creation_time' in df.columns and 'od_end_time' in df.columns:
        start = pd.to_datetime(df['trip_creation_time'], errors='coerce')
        end = pd.to_datetime(df['od_end_time'], errors='coerce')
        
        valid_times = (end - start).dropna().dt.total_seconds() / 3600
        if not valid_times.empty:
            avg_transit = valid_times.mean()
            report += f"- **Average Transit Time:** {avg_transit:.2f} hours\n"
            report += "  - *Formula:* Mean of (od_end_time - trip_creation_time) in hours\n"
            report += "  - *Source Columns:* `trip_creation_time`, `od_end_time`\n\n"
        
    if 'is_cutoff' in df.columns:
        # BUG FIX: Safely handle nulls and string-based booleans
        valid_data = df['is_cutoff'].dropna()
        if not valid_data.empty:
            is_true = valid_data.astype(str).str.lower().isin(['true', '1', 't', 'yes'])
            cutoff_rate = (is_true.sum() / len(valid_data)) * 100
            report += f"- **Trip Cutoff (Failure) Rate:** {cutoff_rate:.2f}%\n"
            report += "  - *Formula:* (Count of True / Total Valid Records) * 100\n"
            report += "  - *Source Column:* `is_cutoff`\n\n"
        
    return report

def calc_route_efficiency(df):
    """Calculates Route deviation with traceability."""
    report = "\n#### 🗺️ Route Efficiency KPIs\n"
    
    if 'actual_distance_to_destination' in df.columns and 'osrm_distance' in df.columns:
        actual_dist = df['actual_distance_to_destination'].sum()
        planned_dist = df['osrm_distance'].sum()
        
        if planned_dist > 0:
            deviation = ((actual_dist - planned_dist) / planned_dist) * 100
            report += f"- **Total Route Deviation:** {deviation:.2f}%\n"
            report += "  - *Formula:* ((Sum Actual Dist - Sum Planned Dist) / Sum Planned Dist) * 100\n"
            report += "  - *Source Columns:* `actual_distance_to_destination`, `osrm_distance`\n\n"
            
    if 'factor' in df.columns:
        avg_factor = df['factor'].dropna().mean()
        report += f"- **Average Routing Factor:** {avg_factor:.2f}\n"
        report += "  - *Formula:* Mean of routing factor metric\n"
        report += "  - *Source Column:* `factor`\n"
        report += "  - *System Warning:* Semantic business definition of 'factor' is not strictly defined in schema.\n\n"
        
    return report

def generate_dynamic_kpis(df):
    """Scans the dataframe columns and generates grouped, traceable KPIs."""
    print("🚦 Scanning columns for Traceable KPI Engine...")
    columns = set(df.columns)
    
    final_kpi_text = "### 📊 2. Core Operational KPIs (System Generated & Traceable)\n"
    kpis_generated = False
    
    if {'trip_creation_time', 'od_end_time', 'is_cutoff'}.intersection(columns):
        final_kpi_text += calc_sla_performance(df)
        kpis_generated = True
        
    if {'actual_distance_to_destination', 'osrm_distance', 'factor'}.intersection(columns):
        final_kpi_text += calc_route_efficiency(df)
        kpis_generated = True
        
    if not kpis_generated:
        final_kpi_text += "- *Insufficient columns to generate advanced logistics KPIs.*\n"
        
    return final_kpi_text

def run_logistics_analysis(payload, client, df=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")
    
    kpi_text = generate_dynamic_kpis(df) if df is not None else ""
    
    with open(prompt_path, "r", encoding="utf-8") as file:
        raw_prompt = file.read()
        
    final_prompt = raw_prompt.format(data_payload=payload + "\n\n" + kpi_text)
    
    response = client.chat.completions.create(
        model="openrouter/free", 
        messages=[
            {"role": "system", "content": "You are a pragmatic, highly experienced Operations Analytics Consultant."},
            {"role": "user", "content": final_prompt}
        ],
    )
    return response.choices[0].message.content
