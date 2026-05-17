import os
from .kpis import calc_sla_performance
from .route_analysis import calc_route_efficiency, calc_hub_intelligence, calc_cost_efficiency

def generate_dynamic_kpis(df):
    """Aggregates all structured KPIs from sub-modules and renders the Markdown Table."""
    print("🚦 Generating Traceable KPI Engine Table...")
    all_kpis = []
    
    all_kpis.extend(calc_sla_performance(df))
    all_kpis.extend(calc_route_efficiency(df))
    all_kpis.extend(calc_hub_intelligence(df))
    all_kpis.extend(calc_cost_efficiency(df))
    
    if not all_kpis:
        return "- *Insufficient columns to generate advanced logistics KPIs.*\n"
        
    table_md = "### 📊 2. Core Operational KPIs (Traceable & Explainable)\n\n"
    table_md += "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    table_md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for kpi in all_kpis:
        table_md += f"| {kpi['category']} | **{kpi['name']}** | `{kpi['value']}` | *{kpi['formula']}* | {kpi['source']} | {kpi['confidence']} | {kpi['warnings']} |\n"
        
    return table_md

def run_logistics_analysis(payload, client, df=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")
    
    # 1. Generate KPIs
    kpi_table = generate_dynamic_kpis(df) if df is not None else ""
    print(f"⚙️ DEBUG: Generated KPI Table ({len(kpi_table)} characters)")
    
    # 2. Prepare Prompt
    with open(prompt_path, "r", encoding="utf-8") as file:
        raw_prompt = file.read()
        
    final_prompt = raw_prompt.format(data_payload=payload)
    
    # 3. Call AI
    print("🧠 Requesting Governed Strategic Insights...")
    try:
        response = client.chat.completions.create(
            model="openrouter/free", 
            messages=[
                {"role": "system", "content": "You are a pragmatic, highly experienced Operations Analytics Consultant."},
                {"role": "user", "content": final_prompt}
            ],
        )
        ai_raw_report = response.choices[0].message.content
        print("✅ DEBUG: AI responded successfully.")
    except Exception as e:
        print(f"❌ DEBUG: AI API Call Failed! Error: {e}")
        return "ERROR: AI failed to generate response."
    
    # 4. BULLETPROOF INJECTION
    if "{{INSERT_KPIS_HERE}}" in ai_raw_report:
        print("🔗 DEBUG: Placeholder found! Injecting KPIs...")
        final_stitched_report = ai_raw_report.replace("{{INSERT_KPIS_HERE}}", kpi_table)
    else:
        print("⚠️ DEBUG: AI forgot the placeholder. Forcing KPIs to the bottom of the report.")
        final_stitched_report = ai_raw_report + "\n\n" + kpi_table
        
    return final_stitched_report
