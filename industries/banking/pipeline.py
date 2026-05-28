import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine # 👈 IMPORT ADDED

# Import your local microservices
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
    for module in [
        calc_account_metrics, calc_balance_metrics, calc_deposit_metrics, 
        calc_loan_metrics, calc_customer_metrics, calc_fee_metrics, 
        calc_compliance_metrics, calc_branch_metrics
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Banking module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    if not kpis:
        return "*Insufficient columns to generate advanced banking KPIs.*"
        
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_banking_analysis(payload, clients, df):
    # 1. Generate Raw KPIs locally
    raw_kpis = generate_dynamic_kpis(df)
    
    # 2. 🛑 DEDUPLICATE (Fixes Issue 5) 🛑
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    
    # 3. Build Markdown using the clean list
    kpi_markdown = build_markdown_table(final_kpis)
    
    # 4. Define Paths
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    # 5. Hand off to the Master Orchestrator
    return run_master_orchestrator(
        industry_name="banking",
        kpi_list=final_kpis,       # 👈 Pass the clean list
        kpi_markdown=kpi_markdown, # 👈 Pass the clean markdown
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        sys_prompt_path=sys_prompt_path
    )
