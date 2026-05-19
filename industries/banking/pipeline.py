import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential

# Import all your new banking specialists
from .account_analysis import calc_account_metrics
from .deposit_analysis import calc_deposit_metrics
from .loan_analysis import calc_loan_metrics
from .customer_analysis import calc_customer_metrics
from .fee_analysis import calc_fee_metrics
from .compliance_analysis import calc_compliance_metrics
from .branch_analysis import calc_branch_metrics

def generate_dynamic_kpis(df):
    """Executes all Banking KPI modules safely."""
    all_kpis = []
    modules = [
        calc_account_metrics, calc_deposit_metrics, calc_loan_metrics,
        calc_customer_metrics, calc_fee_metrics, calc_compliance_metrics,
        calc_branch_metrics
    ]
    
    for module in modules:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: {module.__name__} failed: {e}")
            
    return all_kpis

def build_markdown_table(kpis):
    """Formats the KPI list into a Markdown table."""
    if not kpis: return "No valid banking KPIs calculated."
    md_table = "| Category | Metric | Value | Confidence | Warnings |\n|---|---|---|---|---|\n"
    for kpi in kpis:
        md_table += f"| {kpi.get('category','')} | **{kpi.get('name','')}** | {kpi.get('value','')} | {kpi.get('confidence','')} | {kpi.get('warnings','None')} |\n"
    return md_table

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_gemini_with_retry(client, final_prompt):
    return client.chat.completions.create(
        model="gemini-2.5-flash", 
        messages=[
            {"role": "system", "content": "You are an elite Banking & Financial Risk Consultant."},
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.1 # Very low temp for financial accuracy
    )

def run_banking_analysis(payload, client, df):
    """The main orchestrator for the Banking module."""
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except json.JSONDecodeError: payload = {"raw_data": payload} 
            
    payload['kpi_results'] = kpi_list
    
    # Ensure you create a prompt.txt inside industries/banking/
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    if not os.path.exists(prompt_path):
        return kpi_markdown # Fallback if prompt is missing
        
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
        
    final_prompt = prompt_template.replace('{data_payload}', json.dumps(payload, indent=2))
    
    print("🧠 Consulting AI Banking Analyst...")
    try:
        response = call_gemini_with_retry(client, final_prompt)
        report_content = response.choices[0].message.content
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
    
    return report_content.replace('{{INSERT_KPIS_HERE}}', kpi_markdown)
