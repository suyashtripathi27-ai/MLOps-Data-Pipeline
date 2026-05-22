import os
import json
from utils.llm_router import execute_with_fallback
from .account_analysis import calc_account_metrics
from .balance_analysis import calc_balance_metrics
from .deposit_analysis import calc_deposit_metrics
from .loan_analysis import calc_loan_metrics
from .customer_analysis import calc_customer_metrics
from .fee_analysis import calc_fee_metrics
from .compliance_analysis import calc_compliance_metrics
from .branch_analysis import calc_branch_metrics

def generate_dynamic_kpis(df):
    """Executes all KPI modules dynamically and returns a list of dictionaries."""
    all_kpis = []
    # Safely collect KPIs from all sub-modules
    for module in [
        calc_account_metrics, 
        calc_balance_metrics,
        calc_deposit_metrics, 
        calc_loan_metrics, 
        calc_customer_metrics, 
        calc_fee_metrics, 
        calc_compliance_metrics, 
        calc_branch_metrics
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Banking module {module.__name__} failed: {e}")
    return all_kpis

def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced banking KPIs.*"
        
    md_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in kpis:
        md_table += f"| {kpi.get('category', '')} | **{kpi.get('name', '')}** | `{kpi.get('value', '')}` | *{kpi.get('formula', '')}* | `{kpi.get('source', '')}` | {kpi.get('confidence', 'N/A')} | {kpi.get('warnings', 'None')} |\n"
    return md_table

def run_banking_analysis(payload, clients, df): 
    """The central orchestration layer for Banking."""
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
    system_prompt = "You are an elite Banking & Financial Risk Consultant."
    
    print("🧠 Consulting AI Banking Analyst...")
    try:
        report_content = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
    
    return report_content.replace('{{INSERT_KPIS_HERE}}', kpi_markdown)
