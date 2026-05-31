import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine
from utils.prompt_engine import generate_v3_system_prompt 

from .account_analysis import calc_account_metrics
from .balance_analysis import calc_balance_metrics
from .deposit_analysis import calc_deposit_metrics
from .loan_analysis import calc_loan_metrics
from .customer_analysis import calc_customer_metrics
from .fee_analysis import calc_fee_metrics
from .compliance_analysis import calc_compliance_metrics
from .branch_analysis import calc_branch_metrics

def generate_dynamic_kpis(df):
    all_kpis = []
    for module in [calc_account_metrics, calc_balance_metrics, calc_deposit_metrics, 
                   calc_loan_metrics, calc_customer_metrics, calc_fee_metrics, 
                   calc_compliance_metrics, calc_branch_metrics]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Banking module {module.__name__} failed: {e}")
    return all_kpis

def build_markdown_table(kpis):
    if not kpis: return "*Insufficient columns to generate advanced banking KPIs.*"
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md

def run_banking_analysis(payload, clients, df):
    raw_kpis = generate_dynamic_kpis(df)
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    system_prompt = generate_v3_system_prompt("banking")
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    
    return run_master_orchestrator(
        industry_name="banking",
        kpi_list=final_kpis,
        kpi_markdown=kpi_markdown,
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        system_prompt_text=system_prompt
    )
