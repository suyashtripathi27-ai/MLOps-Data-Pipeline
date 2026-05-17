import os
import pandas as pd

# ==========================================
# 🛡️ KPI METADATA & CONFIDENCE ENGINE
# ==========================================

def evaluate_kpi_confidence(df, columns):
    """
    Evaluates the reliability of specific columns used for a KPI.
    Returns a Confidence Level and a list of Warnings.
    """
    warnings = []
    confidence = "High"
    
    for col in columns:
        if col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 0:
                warnings.append(f"{missing_pct:.1f}% missing in `{col}`")
                
            if missing_pct >= 20:
                confidence = "Low"
            elif missing_pct > 5 and confidence != "Low":
                confidence = "Medium"
                
    warning_str = ", ".join(warnings) if warnings else "None"
    return confidence, warning_str

# ==========================================
# 🧩 STRUCTURED KPI CALCULATION MODULES
# ==========================================

def calc_sla_performance(df):
    """Calculates SLA KPIs and returns them as structured dictionaries."""
    kpis = []
    
    if 'trip_creation_time' in df.columns and 'od_end_time' in df.columns:
        start = pd.to_datetime(df['trip_creation_time'], errors='coerce')
        end = pd.to_datetime(df['od_end_time'], errors='coerce')
        
        valid_times = (end - start).dropna().dt.total_seconds() / 3600
        if not valid_times.empty:
            avg_transit = valid_times.mean()
            conf, warns = evaluate_kpi_confidence(df, ['trip_creation_time', 'od_end_time'])
            
            kpis.append({
                "category": "⏱️ SLA & Delivery",
                "name": "Average Transit Time",
                "value": f"{avg_transit:.2f} hrs",
                "formula": "Mean(od_end_time - trip_creation_time)",
                "source": "`trip_creation_time`, `od_end_time`",
                "confidence": conf,
                "warnings": warns
            })
            
    if 'is_cutoff' in df.columns:
        valid_data = df['is_cutoff'].dropna()
        if not valid_data.empty:
            is_true = valid_data.astype(str).str.lower().isin(['true', '1', 't', 'yes'])
            cutoff_rate = (is_true.sum() / len(valid_data)) * 100
            conf, warns = evaluate_kpi_confidence(df, ['is_cutoff'])
            
            kpis.append({
                "category": "⏱️ SLA & Delivery",
                "name": "Trip Cutoff Rate",
                "value": f"{cutoff_rate:.2f}%",
                "formula": "(True / Total Valid) * 100",
                "source": "`is_cutoff`",
                "confidence": conf,
                "warnings": warns
            })
            
    return kpis

def calc_route_efficiency(df):
    """Calculates Route KPIs and returns them as structured dictionaries."""
    kpis = []
    
    if 'actual_distance_to_destination' in df.columns and 'osrm_distance' in df.columns:
        actual_dist = df['actual_distance_to_destination'].sum()
        planned_dist = df['osrm_distance'].sum()
        
        if planned_dist > 0:
            deviation = ((actual_dist - planned_dist) / planned_dist) * 100
            conf, warns = evaluate_kpi_confidence(df, ['actual_distance_to_destination', 'osrm_distance'])
            
            kpis.append({
                "category": "🗺️ Route Efficiency",
                "name": "Total Route Deviation",
                "value": f"{deviation:.2f}%",
                "formula": "((Actual - Planned) / Planned) * 100",
                "source": "`actual_...`, `osrm_...`",
                "confidence": conf,
                "warnings": warns
            })
            
    if 'factor' in df.columns:
        avg_factor = df['factor'].dropna().mean()
        conf, warns = evaluate_kpi_confidence(df, ['factor'])
        # Hardcode a semantic warning for ambiguous metrics
        if warns == "None": warns = ""
        warns += " Semantic definition of 'factor' is ambiguous."
        
        kpis.append({
            "category": "🗺️ Route Efficiency",
            "name": "Average Routing Factor",
            "value": f"{avg_factor:.2f}",
            "formula": "Mean(factor)",
            "source": "`factor`",
            "confidence": conf,
            "warnings": warns.strip()
        })
        
    return kpis

# ==========================================
# 🚦 THE KPI RENDERER
# ==========================================

def generate_dynamic_kpis(df):
    """Aggregates all structured KPIs and renders a Markdown Table."""
    print("🚦 Generating Traceable KPI Engine Table...")
    all_kpis = []
    
    # 1. Gather all structured KPIs
    all_kpis.extend(calc_sla_performance(df))
    all_kpis.extend(calc_route_efficiency(df))
    
    if not all_kpis:
        return "- *Insufficient columns to generate advanced logistics KPIs.*\n"
        
    # 2. Render the Enterprise Markdown Table
    table_md = "### 📊 2. Core Operational KPIs (Traceable & Explainable)\n\n"
    table_md += "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    table_md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for kpi in all_kpis:
        table_md += f"| {kpi['category']} | **{kpi['name']}** | `{kpi['value']}` | *{kpi['formula']}* | {kpi['source']} | {kpi['confidence']} | {kpi['warnings']} |\n"
        
    return table_md

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================

def run_logistics_analysis(payload, client, df=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")
    
    kpi_table = generate_dynamic_kpis(df) if df is not None else ""
    
    with open(prompt_path, "r", encoding="utf-8") as file:
        raw_prompt = file.read()
        
    final_prompt = raw_prompt.format(data_payload=payload)
    
    print("🧠 Requesting Governed Strategic Insights...")
    response = client.chat.completions.create(
        model="openrouter/free", 
        messages=[
            {"role": "system", "content": "You are a pragmatic, highly experienced Operations Analytics Consultant."},
            {"role": "user", "content": final_prompt}
        ],
    )
    
    ai_raw_report = response.choices[0].message.content
    final_stitched_report = ai_raw_report.replace("{{INSERT_KPIS_HERE}}", kpi_table)
    
    return final_stitched_report
