import os
from .kpis import calc_sla_performance
from .route_analysis import calc_route_efficiency, calc_cost_efficiency
from .hub_analysis import calc_hub_intelligence
from .fleet_analysis import calc_fleet_economics  # <-- NEW FLEET IMPORT
from .charts import generate_logistics_charts

def generate_dynamic_kpis(df):
    all_kpis = []
    
    # Run Last-Mile KPIs (Safe to run: will skip if columns are missing)
    all_kpis.extend(calc_sla_performance(df))
    all_kpis.extend(calc_route_efficiency(df))
    all_kpis.extend(calc_cost_efficiency(df))
    all_kpis.extend(calc_hub_intelligence(df))
    
    # Run Heavy Fleet KPIs (NEW)
    all_kpis.extend(calc_fleet_economics(df))
    
    if not all_kpis:
        return "*Insufficient columns to generate advanced logistics KPIs.*"
        
    markdown_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    markdown_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in all_kpis:
        markdown_table += f"| {kpi['category']} | **{kpi['name']}** | `{kpi['value']}` | *{kpi['formula']}* | `{kpi['source']}` | {kpi['confidence']} | {kpi['warnings']} |\n"
    return markdown_table

def run_logistics_analysis(payload, client, df=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")
    
    # Generate KPIs and Charts
    if df is not None:
        kpi_table = generate_dynamic_kpis(df)
        generate_logistics_charts(df)
    else:
        kpi_table = ""
        
    print(f"⚙️ DEBUG: Generated KPI Table ({len(kpi_table)} characters)")
    
    with open(prompt_path, "r", encoding="utf-8") as file:
        raw_prompt = file.read()
        
    final_prompt = raw_prompt.format(data_payload=payload)
    
    print("🧠 Requesting Governed Strategic Insights...")
    try:
        response = client.chat.completions.create(
            model="openrouter/free", 
            messages=[
                {"role": "system", "content": "You are a pragmatic, highly experienced Operations Analytics Consultant. Focus only on the provided data context."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.2
        )
        ai_raw_report = response.choices[0].message.content
        print("✅ DEBUG: AI responded successfully.")
    except Exception as e:
        print(f"❌ DEBUG: AI API Call Failed! Error: {e}")
        return "ERROR: AI failed to generate response."
    
    if "{{INSERT_KPIS_HERE}}" in ai_raw_report:
        print("🔗 DEBUG: Double-brace placeholder found! Injecting KPIs...")
        final_stitched_report = ai_raw_report.replace("{{INSERT_KPIS_HERE}}", kpi_table)
    elif "{INSERT_KPIS_HERE}" in ai_raw_report:
        print("🔗 DEBUG: Single-brace placeholder found! Injecting KPIs...")
        final_stitched_report = ai_raw_report.replace("{INSERT_KPIS_HERE}", kpi_table)
    else:
        print("⚠️ DEBUG: AI completely forgot the placeholder. Forcing KPIs to the bottom of the report.")
        final_stitched_report = ai_raw_report + "\n\n### Traceable KPIs\n" + kpi_table
        
    return final_stitched_report
