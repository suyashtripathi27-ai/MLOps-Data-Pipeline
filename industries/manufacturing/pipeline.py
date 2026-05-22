import json
import os

from utils.llm_router import execute_with_fallback
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


def generate_dynamic_kpis(df):
    """Run all manufacturing KPI modules and collect results."""
    all_kpis = []
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
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Manufacturing module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    if not kpis:
        return "*No manufacturing KPIs could be computed from the provided dataset.*"

    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_manufacturing_analysis(payload, clients, df):
    """The central orchestration layer for Manufacturing."""
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"raw_data": payload}

    payload["kpi_results"] = kpi_list

    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
    if not os.path.exists(prompt_path):
        return f"⚠️ Warning: prompt.txt missing.\n\n{kpi_markdown}"

    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    final_prompt = prompt_template.replace("{data_payload}", json.dumps(payload, indent=2))
    system_prompt = "You are a world-class Manufacturing Operations, Production Planning, and Quality Assurance Consultant."

    print("🧠 Consulting AI Manufacturing Operations Analyst...")
    try:
        report_content = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup KPI Table\n{kpi_markdown}"

    # Force the KPI table into the final output safely
    final_report = f"{report_content}\n\n### 📊 Detailed Operational KPIs\n{kpi_markdown}"
    return final_report
