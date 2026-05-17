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
    return ai_raw_report.replace("{{INSERT_KPIS_HERE}}", kpi_table)
