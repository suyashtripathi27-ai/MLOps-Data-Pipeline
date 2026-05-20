import os
import json
from utils.llm_router import execute_with_fallback

# 🧩 Import the Microservices
from .profitability_analysis import calc_profitability_metrics
from .cashflow_analysis import calc_cashflow_metrics
from .liquidity_analysis import calc_liquidity_solvency_metrics

def generate_dynamic_kpis(df):
    all_kpis = []
    modules = [
        calc_profitability_metrics, 
        calc_cashflow_metrics, 
        calc_liquidity_solvency_metrics
    ]
    
    for module in modules:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Finance module {module.__name__} failed: {e}")
            
    return all_kpis

def build_markdown_table(kpis):
    if not kpis:
        return "*Insufficient columns to generate advanced financial KPIs.*"
        
    md_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in kpis:
        md_table += f"| {kpi.get('category', '')} | **{kpi.get('name', '')}** | `{kpi.get('value', '')}` | *{kpi.get('formula', '')}* | `{kpi.get('source', '')}` | {kpi.get('confidence', 'N/A')} | {kpi.get('warnings', 'None')} |\n"
    return md_table

def run_finance_analysis(payload, clients, df): 
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except json.JSONDecodeError: payload = {"raw_data": payload} 
            
    payload['kpi_results'] = kpi_list
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    if not os.path.exists(prompt_path): 
        return f"⚠️ Warning: prompt.txt missing.\n\n{kpi_markdown}"
        
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
        
    final_prompt = prompt_template.replace('{data_payload}', json.dumps(payload, indent=2))
    system_prompt = "You are an elite Chief Financial Officer (CFO) and Quantitative Risk Analyst."
    
    print("🧠 Consulting AI Financial Auditor...")
    try:
        report_content = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
    
    return report_content.replace('{{INSERT_KPIS_HERE}}', kpi_markdown)
