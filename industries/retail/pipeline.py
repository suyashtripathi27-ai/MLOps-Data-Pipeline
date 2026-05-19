import os
import json
from .inventory_analysis import calc_inventory_metrics
from .sales_analysis import calc_sales_metrics

def generate_dynamic_kpis(df):
    """Executes all Retail KPI modules dynamically."""
    all_kpis = []
    all_kpis.extend(calc_inventory_metrics(df))
    all_kpis.extend(calc_sales_metrics(df))
    return all_kpis

def build_markdown_table(kpis):
    """Formats the KPI JSON list into a Markdown table."""
    if not kpis:
        return "No valid KPIs could be calculated from this dataset."
        
    md_table = "| Category | Metric | Value | Source |\n"
    md_table += "|---|---|---|---|\n"
    for kpi in kpis:
        md_table += f"| {kpi.get('category','')} | **{kpi.get('name','')}** | {kpi.get('value','')} | {kpi.get('source','')} |\n"
    return md_table

def run_retail_analysis(payload, client, df):
    """The main orchestrator for the Retail module."""
    
    # 1. Run the Python Math layer
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    # 2. Append the Technical Diagnostics to the Payload
    payload['kpi_results'] = kpi_list
    
    # 3. Load the Retail Prompt
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
        
    final_prompt = prompt_template.replace('{data_payload}', json.dumps(payload, indent=2))
    
    # 4. Call the LLM
    print("🧠 Consulting AI Retail Analyst...")
    response = client.chat.completions.create(
        model="openrouter/auto", 
        messages=[{"role": "user", "content": final_prompt}]
    )
    
    report_content = response.choices[0].message.content
    
    # 5. Inject the strict Markdown table
    final_report = report_content.replace('{{INSERT_KPIS_HERE}}', kpi_markdown)
    
    return final_report
