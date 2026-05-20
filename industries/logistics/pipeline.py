import os
from .kpis import calc_sla_performance
from .route_analysis import calc_route_efficiency, calc_cost_efficiency
from .hub_analysis import calc_hub_intelligence
from .fleet_analysis import calc_fleet_economics 
from .freight_analysis import calc_freight_metrics
from .iot_analysis import calc_iot_sensor_metrics
from .charts import generate_logistics_charts
from utils.llm_router import execute_with_fallback

def generate_dynamic_kpis(df):
    all_kpis = [] 
    all_kpis.extend(calc_sla_performance(df))
    all_kpis.extend(calc_route_efficiency(df))
    all_kpis.extend(calc_cost_efficiency(df))
    all_kpis.extend(calc_hub_intelligence(df))
    all_kpis.extend(calc_fleet_economics(df))
    all_kpis.extend(calc_iot_sensor_metrics(df))
    all_kpis.extend(calc_freight_metrics(df))
    
    if not all_kpis:
        return "*Insufficient columns to generate advanced logistics KPIs.*"
        
    markdown_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    markdown_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in all_kpis:
        markdown_table += f"| {kpi['category']} | **{kpi['name']}** | `{kpi['value']}` | *{kpi['formula']}* | `{kpi['source']}` | {kpi['confidence']} | {kpi['warnings']} |\n"
    return markdown_table

def run_logistics_analysis(payload, clients, df): 
    """The central orchestration layer for Logistics."""
    kpi_list = generate_dynamic_kpis(df) # Assuming this function is above
    kpi_markdown = build_markdown_table(kpi_list) # Assuming this function is above
    
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except json.JSONDecodeError: payload = {"raw_data": payload} 
            
    payload['kpi_results'] = kpi_list
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    if not os.path.exists(prompt_path): return kpi_markdown
        
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
        
    final_prompt = prompt_template.replace('{data_payload}', json.dumps(payload, indent=2))
    system_prompt = "You are a pragmatic, highly experienced Supply Chain and Operations Analytics Consultant."
    
    print("🧠 Consulting AI Logistics Analyst...")
    try:
        report_content = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
    
    return report_content.replace('{{INSERT_KPIS_HERE}}', kpi_markdown)
