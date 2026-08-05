import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine
from utils.prompt_engine import generate_v3_system_prompt

from .cost_analysis import calc_cost_metrics
from .demand_analysis import calc_demand_metrics
from .downtime_analysis import calc_downtime_metrics
from .efficiency_analysis import calc_efficiency_metrics
from .energy_analysis import calc_energy_metrics
from .forecasting_analysis import calc_forecasting_metrics
from .inventory_analysis import calc_inventory_metrics
from .maintenance_analysis import calc_maintenance_metrics
from .production_analysis import calc_production_metrics
from .quality_analysis import calc_quality_metrics
from .safety_analysis import calc_safety_metrics
from .supply_chain_analysis import calc_supply_chain_metrics
from .workforce_analysis import calc_workforce_metrics
from utils.categorical_analysis import calc_universal_categorical_metrics 


def generate_dynamic_kpis(df):
    """Executes all KPI modules dynamically and returns a list of dictionaries."""
    all_kpis = []
    
    # 🛠️ FIXED: Removed the obsolete SemanticValidator block.
    
    for module in [
        calc_production_metrics,
        calc_quality_metrics,
        calc_inventory_metrics,
        calc_downtime_metrics,
        calc_maintenance_metrics,
        calc_supply_chain_metrics,
        calc_workforce_metrics,
        calc_efficiency_metrics,
        calc_energy_metrics,
        calc_forecasting_metrics,
        calc_cost_metrics,
        calc_demand_metrics,
        calc_safety_metrics,
        calc_universal_categorical_metrics # 👈 FIXED: Added to the execution list!
    ]:
        try:
            result = module(df)
            # 🛠️ FIXED: Added safety checks in case a module returns a single dict instead of a list
            if isinstance(result, dict):
                all_kpis.append(result)
            elif isinstance(result, list):
                all_kpis.extend(result)
        except Exception as e:
            print(f"⚠️ Warning: Manufacturing module {module.__name__} failed: {e}")
            
    return all_kpis


def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced manufacturing KPIs.*"

    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        if isinstance(k, dict):
            md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_manufacturing_analysis(payload, clients, df): 
    raw_kpis = generate_dynamic_kpis(df)
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    
    system_prompt = generate_v3_system_prompt("manufacturing")
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    
    return run_master_orchestrator(
        industry_name="manufacturing", 
        kpi_list=final_kpis,           
        kpi_markdown=kpi_markdown,     
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        system_prompt_text=system_prompt # 👈 FIXED: Updated to match the new Orchestrator
    )
