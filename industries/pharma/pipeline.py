"""
Pharma Industry Analytics Pipeline
"""
import os
import json
from .kpis import generate_pharma_kpis
from .reliability import run_pharma_governance_checks
from utils.llm_router import execute_with_fallback

def generate_dynamic_kpis(df):
    """Executes all pharma KPI modules dynamically."""
    return generate_pharma_kpis(df)

def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced pharma KPIs.*"
        
    md_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in kpis:
        md_table += f"| {kpi.get('category', '')} | **{kpi.get('name', '')}** | `{kpi.get('value', '')}` | *{kpi.get('formula', '')}* | `{kpi.get('source', '')}` | {kpi.get('confidence', 'N/A')} | {kpi.get('warnings', 'None')} |\n"
    return md_table

def run_pharma_analysis(payload, clients, df): # Notice we pass 'clients' plural
    """The central orchestration layer for the Pharma pipeline module."""
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except json.JSONDecodeError: payload = {"raw_data": payload} 
            
    payload['kpi_results'] = kpi_list
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    if not os.path.exists(prompt_path):
        return kpi_markdown
        
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
        
    final_prompt = prompt_template.replace('{data_payload}', json.dumps(payload, indent=2))
    system_prompt = "You are a world-class Life Sciences, Pharmaceutical Operations, and FDA Compliance Consultant."
    
    print("🧠 Consulting AI Pharma Operations Analyst...")
    try:
        # 🛡️ THE MAGIC HAPPENS HERE: We use the fallback engine!
        report_content = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
    
    return report_content.replace('{{INSERT_KPIS_HERE}}', kpi_markdown)
    
    # Build comprehensive report
    final_report = f"""
# 💊 Pharmaceutical Industry Analysis Report

## 📊 KPI Metrics

{kpi_markdown}

## 🏥 Governance & Compliance

{chr(10).join(governance_warnings)}

## 🤖 AI-Powered Strategic Insights

{ai_analysis}

---
*Report Generated: Pharma Analytics Pipeline v1.0*
"""
    
    return final_report
