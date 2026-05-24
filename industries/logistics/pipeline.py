import os
from utils.master_orchestrator import run_master_orchestrator
from utils.semantic_validator import SemanticValidator

from .route_analysis import calc_route_efficiency, calc_cost_efficiency
from .hub_analysis import calc_hub_intelligence
from .fleet_analysis import calc_fleet_economics 
from .freight_analysis import calc_freight_metrics
from .iot_analysis import calc_iot_sensor_metrics
from .sla_analysis import calc_sla_performance


def generate_dynamic_kpis(df):
    """Executes all KPI modules dynamically and returns a list of dictionaries."""
    all_kpis = []
    
    # Validate time-based columns in logistics (transit time, delivery delay, etc.)
    validator = SemanticValidator()
    time_columns = {
        'transit_time_days', 'transit_time_hours', 'transit_time_minutes',
        'delivery_delay_hours', 'delivery_delay_days', 'loading_dock_time',
        'unloading_time', 'dwell_time', 'wait_time', 'idle_time'
    }
    
    for col in df.columns:
        if col.lower() in time_columns or 'time' in col.lower() or 'duration' in col.lower():
            if not validator.is_valid_duration(df[col]):
                print(f"⚠️ Warning: Column '{col}' may not be valid elapsed time data")
    
    for module in [
        calc_sla_performance,
        calc_route_efficiency,
        calc_cost_efficiency, 
        calc_hub_intelligence,
        calc_fleet_economics,
        calc_iot_sensor_metrics,
        calc_freight_metrics
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Logistics module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced logistics KPIs.*"

    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_logistics_analysis(payload, clients, df):
    # 1. Generate KPIs locally
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    # 2. Define Paths
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    # 3. Hand off to the Master Orchestrator
    return run_master_orchestrator(
        industry_name="logistics",
        kpi_list=kpi_list,
        kpi_markdown=kpi_markdown,
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        sys_prompt_path=sys_prompt_path
    )
