"""
Logistics Industry Pipeline: Fleet, Freight, Hub, and SLA Analytics.
"""
import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine # 👈 Added Deduplication Engine

# Import modules
from .route_analysis import calc_route_efficiency, calc_cost_efficiency
from .hub_analysis import calc_hub_intelligence
from .fleet_analysis import calc_fleet_economics 
from .freight_analysis import calc_freight_metrics
from .iot_analysis import calc_iot_sensor_metrics
from .sla_analysis import calc_sla_performance

def generate_dynamic_kpis(df):
    all_kpis = []
    # Dynamic orchestration of logistics modules
    for module in [
        calc_sla_performance, calc_route_efficiency, calc_cost_efficiency, 
        calc_hub_intelligence, calc_fleet_economics, calc_iot_sensor_metrics, 
        calc_freight_metrics
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Logistics module {module.__name__} failed: {e}")
    return all_kpis

def run_logistics_analysis(payload, clients, df):
    # 1. Generate Raw KPIs
    raw_kpis = generate_dynamic_kpis(df)
    
    # 2. 🛑 DEDUPLICATE (Fixes Issue 5) 🛑
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    
    # 3. Build Markdown
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in final_kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    
    return run_master_orchestrator(
        industry_name="logistics",
        kpi_list=final_kpis,
        kpi_markdown=md,
        payload=payload,
        clients=clients,
        prompt_path=os.path.join(os.path.dirname(__file__), 'prompt.txt'),
        sys_prompt_path=os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    )
