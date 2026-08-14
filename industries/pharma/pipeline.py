import os
import sys
import pandas as pd

# 1. Path Bootstrapping (Ensures utils can be imported cleanly)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine
from utils.validator import SemanticValidator  # 👈 IMPORT ADDED

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
    
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return all_kpis

    # Validate time-based columns in pharma
    validator = SemanticValidator()
    time_columns = {
        'trial_duration_days', 'trial_duration_months', 'time_to_hire_days',
        'employee_tenure_months', 'shelf_life_days', 'manufacturing_duration',
        'storage_duration', 'delivery_time', 'approval_timeline'
    }
    
    for col in df.columns:
        if col.lower() in time_columns or 'duration' in col.lower() or 'tenure' in col.lower():
            # Fixed tuple unpacking: (bool, message)
            is_valid, msg = validator.is_valid_duration(df[col])
            if not is_valid:
                print(f"⚠️ Warning: Column '{col}' may not be valid elapsed time data ({msg})")
    
    modules = [
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
    ]
    
    for module in modules:
        try:
            res = module(df)
            if isinstance(res, list):
                all_kpis.extend(res)
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


def run_pharma_analysis(payload, clients, df): 
    raw_kpis = generate_dynamic_kpis(df)
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')

    return run_master_orchestrator(
        industry_name="pharma", 
        kpi_list=final_kpis,           
        kpi_markdown=kpi_markdown,     
        payload=payload,
        clients=clients,
        prompt_path=prompt_path
    )
