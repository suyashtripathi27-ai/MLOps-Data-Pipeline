import os
from utils.master_orchestrator import run_master_orchestrator

from .route_analysis import calc_route_efficiency, calc_cost_efficiency
from .hub_analysis import calc_hub_intelligence
from .fleet_analysis import calc_fleet_economics 
from .freight_analysis import calc_freight_metrics
from .iot_analysis import calc_iot_sensor_metrics
from .sla_analysis import calc_sla_performance

def generate_dynamic_kpis(df):
    all_kpis = []
    for module in [
        calc_sla_performance, calc_route_efficiency, calc_cost_efficiency, 
        calc_hub_intelligence, calc_fleet_economics, calc_iot_sensor_metrics, calc_freight_metrics
    ]:
        try: all_kpis.extend(module(df))
        except Exception as e: print(f"⚠️ Warning: Logistics module {module.__name__} failed: {e}")
    return all_kpis

def build_markdown_table(kpis):
    if not kpis: return "*Insufficient columns to generate advanced logistics KPIs.*"
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis: md += f"| {k.get('category', '')} | **{k.get('name', '')}** | `{kpi.get('value', '')}` | *{kpi.get('formula', '')}* | `{kpi.get('source', '')}` | {kpi.get('confidence', 'N/A')} | {kpi.get('warnings', 'None')} |\n"
    return md

def run_logistics_analysis(payload, clients, df): 
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    return run_master_orchestrator(
        industry_name="logistics",
        kpi_list=kpi_list, kpi_markdown=kpi_markdown,
        payload=payload, clients=clients,
        prompt_path=prompt_path, sys_prompt_path=sys_prompt_path
    )
