import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine 
from utils.prompt_engine import generate_v3_system_prompt
from .customer_analysis import calc_customer_metrics
from .department_analysis import calc_department_metrics
from .inventory_analysis import calc_inventory_metrics
from .pricing_analysis import calc_pricing_metrics
from .promotion_analysis import calc_promotion_metrics
from .sales_analysis import calc_sales_metrics
from .seasonality_analysis import calc_seasonality_metrics
from .store_analysis import calc_store_metrics
from .workforce_analysis import calc_workforce_metrics

def generate_dynamic_kpis(df):
    all_kpis = []
    for module in [
        calc_sales_metrics, calc_store_metrics, calc_department_metrics,
        calc_inventory_metrics, calc_seasonality_metrics, calc_pricing_metrics,
        calc_customer_metrics, calc_promotion_metrics, calc_workforce_metrics
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Retail module {module.__name__} failed: {e}")
    return all_kpis

def build_markdown_table(kpis):
    if not kpis:
        return "*Insufficient columns to generate advanced retail KPIs.*"
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md

def run_retail_analysis(payload, clients, df):
    raw_kpis = generate_dynamic_kpis(df)
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    system_prompt = generate_v3_system_prompt("retail")
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    
    return run_master_orchestrator(
        industry_name="retail",
        kpi_list=final_kpis,       
        kpi_markdown=kpi_markdown, 
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        system_prompt_text=system_prompt
    )
