import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine
from utils.prompt_engine import generate_v3_system_prompt

from .route_analysis import calc_route_efficiency, calc_cost_efficiency
from .hub_analysis import calc_hub_intelligence
from .fleet_analysis import calc_fleet_economics 
from .freight_analysis import calc_freight_metrics
from .iot_analysis import calc_iot_sensor_metrics
from .sla_analysis import calc_sla_performance
from utils.categorical_analysis import calc_universal_categorical_metrics

def generate_dynamic_kpis(df):
    all_kpis = []
    for module in [
        calc_sla_performance, calc_route_efficiency, calc_cost_efficiency, 
        calc_hub_intelligence, calc_fleet_economics, calc_iot_sensor_metrics, 
        calc_freight_metrics, calc_universal_categorical_metrics
    ]:
        try:
            result = module(df)
            # 🛡️ DEFENSIVE FIX: Handle both dicts and lists safely!
            if isinstance(result, dict):
                all_kpis.append(result)
            elif isinstance(result, list):
                all_kpis.extend(result)
        except Exception as e:
            print(f"⚠️ Warning: Logistics module {module.__name__} failed: {e}")
    return all_kpis

def build_markdown_table(kpis):
    if not kpis:
        return "*Insufficient columns to generate advanced logistics KPIs.*"
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        # 🛡️ DEFENSIVE FIX: Ensure we only parse actual dictionaries
        if isinstance(k, dict):
            md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md

def run_logistics_analysis(payload, clients, df):
    raw_kpis = generate_dynamic_kpis(df)
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    
    # 🧠 V3 PROMPT INJECTION
    system_prompt = generate_v3_system_prompt("logistics")
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    
    return run_master_orchestrator(
        industry_name="logistics",
        kpi_list=final_kpis,
        kpi_markdown=kpi_markdown,
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        system_prompt_text=system_prompt
    )
