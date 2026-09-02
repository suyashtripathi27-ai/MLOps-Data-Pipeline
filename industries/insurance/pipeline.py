import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine
from utils.prompt_engine import generate_v3_system_prompt

from .underwriting_analysis import calc_underwriting_metrics
from .claims_analysis import calc_claims_metrics
from .fraud_analysis import calc_fraud_metrics
from .policy_analysis import calc_policy_metrics
from utils.categorical_analysis import calc_universal_categorical_metrics


def generate_dynamic_kpis(df):
    all_kpis = []
    for module in [
        calc_underwriting_metrics,
        calc_claims_metrics,
        calc_fraud_metrics,
        calc_policy_metrics,
        calc_universal_categorical_metrics
    ]:
        try:
            result = module(df)
            if isinstance(result, dict):
                all_kpis.append(result)
            elif isinstance(result, list):
                all_kpis.extend(result)
        except Exception as e:
            print(f"⚠️ Warning: Insurance module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    if not kpis:
        return "*Insufficient columns to generate advanced insurance KPIs.*"
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        if isinstance(k, dict):
            md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_insurance_analysis(payload, clients, df):
    raw_kpis = generate_dynamic_kpis(df)
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    system_prompt = generate_v3_system_prompt("insurance")
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')

    return run_master_orchestrator(
        industry_name="insurance",
        kpi_list=final_kpis,
        kpi_markdown=kpi_markdown,
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        system_prompt_text=system_prompt
    )
