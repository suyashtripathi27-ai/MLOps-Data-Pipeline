import os
import json
from utils.llm_router import execute_with_fallback
from .profitability_analysis import calc_profitability_metrics
from .liquidity_analysis import calc_liquidity_metrics
from .expense_analysis import calc_expense_metrics
from .revenue_analysis import calc_revenue_metrics
from .cashflow_analysis import calc_cashflow_metrics
from .risk_analysis import calc_risk_metrics
from .fraud_analysis import calc_fraud_metrics
from .investment_analysis import calc_investment_metrics
from .forecasting_analysis import calc_forecasting_metrics


def generate_dynamic_kpis(df):
    """Run all finance KPI modules and collect results."""
    all_kpis = []
    for module in [
        calc_profitability_metrics,
        calc_liquidity_metrics,
        calc_expense_metrics,
        calc_revenue_metrics,
        calc_cashflow_metrics,
        calc_risk_metrics,
        calc_fraud_metrics,
        calc_investment_metrics,
        calc_forecasting_metrics,
    ]:
        try:
            all_kpis.extend(module(df))
        except Exception as e:
            print(f"⚠️ Warning: Finance module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    if not kpis:
        return "*No finance KPIs could be computed from the provided dataset.*"
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_finance_analysis(payload, clients, df):
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

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    final_prompt = prompt_template.replace("{data_payload}", json.dumps(payload, indent=2))
    system_prompt = "You are a senior Corporate Finance & Treasury Consultant."

    print("🧠 Consulting AI Finance Analyst...")
    try:
        report = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup KPI Table\n{kpi_markdown}"

    return report.replace("{{INSERT_KPIS_HERE}}", kpi_markdown)
