from utils.insight_engine import synthesize_operational_signals
from utils.report_cleaner import clean_report_text
from utils.governance_engine import validate_operational_claims, inject_reliability_warning
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
    # 1. Generate Raw Data
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    # 2. Extract and Prioritize Signals
    signals_dict = synthesize_operational_signals(kpi_list, industry="manufacturing")
    
    # 🔥 TOP CLUSTER FILTERING (NARRATIVE PRIORITIZATION) 🔥
    narrative_blocks = signals_dict.get("PRIORITIZED_NARRATIVE_BLOCKS", {})
    top_3_clusters = dict(list(narrative_blocks.items())[:3])
    
    # Calculate average confidence for governance later
    confidences = [data.get('aggregated_confidence', 1.0) for data in top_3_clusters.values()]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
    
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except:
            payload = {"raw_data": payload}
            
    # Send ONLY the top 3 clusters
    payload['prioritized_signals'] = {"PRIORITIZED_NARRATIVE_BLOCKS": top_3_clusters}
    
    # 3. Load Prompts
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        final_prompt = f.read().replace('{data_payload}', json.dumps(payload, indent=2))
        
    with open(sys_prompt_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    # 4. Generate AI Report
    print("🧠 Synthesizing Executive Intelligence...")
    try:
        raw_report = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
        
    # 5. POST-PROCESSING: Governance & Readability Cleaners
    clean_report = clean_report_text(raw_report)
    safe_report = validate_operational_claims(clean_report)
    final_report = inject_reliability_warning(safe_report, avg_confidence)
    
    # Append the raw data at the bottom
    return f"{final_report}\n\n---\n### 📊 Technical Appendix: Operational KPIs\n{kpi_markdown}"
