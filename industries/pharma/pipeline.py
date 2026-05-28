import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine

from .sales_analysis import calc_pharma_sales_metrics
from .shelf_life_analysis import calc_shelf_life_metrics
from .compliance_analysis import calc_compliance_metrics
from .clinical_trials_analysis import calc_clinical_metrics
from .adverse_events_analysis import calc_adverse_events_metrics
from .forecast_analysis import calc_forecast_metrics
from .product_performance_analysis import calc_product_performance_metrics
from .manufacturing_analysis import calc_manufacturing_metrics
from .supply_chain_analysis import calc_pharma_supply_metrics
from .regulatory_analysis import calc_regulatory_metrics


def generate_dynamic_kpis(df):
    """Executes all KPI modules dynamically and returns a list of dictionaries."""
    all_kpis = []
    
    # Validate time-based columns in pharma (trial duration, time_to_hire, etc.)
    validator = SemanticValidator()
    time_columns = {
        'trial_duration_days', 'trial_duration_months', 'time_to_hire_days',
        'employee_tenure_months', 'shelf_life_days', 'manufacturing_duration',
        'storage_duration', 'delivery_time', 'approval_timeline'
    }
    
    for col in df.columns:
        if col.lower() in time_columns or 'duration' in col.lower() or 'tenure' in col.lower():
            if not validator.is_valid_duration(df[col]):
                print(f"⚠️ Warning: Column '{col}' may not be valid elapsed time data")
    
    for module in [
        calc_pharma_sales_metrics,
        calc_shelf_life_metrics,
        calc_compliance_metrics,
        calc_clinical_metrics,
        calc_adverse_events_metrics,
        calc_forecast_metrics,
        calc_product_performance_metrics,
        calc_manufacturing_metrics,
        calc_pharma_supply_metrics,
        calc_regulatory_metrics
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Pharma module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced pharma KPIs.*"

    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md

def run_manufacturing_analysis(payload, clients, df): # (Do the same for run_pharma_analysis)
    # 1. Generate Raw KPIs locally
    raw_kpis = generate_dynamic_kpis(df)
    
    # 2. 🛑 DEDUPLICATE DIAGNOSTICS (Issue 5 Fix) 🛑
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    
    # 3. Build Markdown using the clean list
    kpi_markdown = build_markdown_table(final_kpis)
    
    # 4. Define Paths
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    # 5. Hand off to the Master Orchestrator
    return run_master_orchestrator(
        industry_name="manufacturing", # (or "pharma")
        kpi_list=final_kpis,           # 👈 Pass the clean list
        kpi_markdown=kpi_markdown,     # 👈 Pass the clean markdown
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        sys_prompt_path=sys_prompt_path
    )
