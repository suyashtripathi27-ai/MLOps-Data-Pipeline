import os
from utils.master_orchestrator import run_master_orchestrator

from .profitability_analysis import calc_profitability_metrics
from .liquidity_analysis import calc_liquidity_metrics
from .expenses_analysis import calc_expense_metrics
from .revenue_analysis import calc_revenue_metrics
from .cashflow_analysis import calc_cashflow_metrics
from .risk_analysis import calc_risk_metrics
from .fraud_analysis import calc_fraud_metrics
from .investment_analysis import calc_investment_metrics
from .forecasting_analysis import calc_forecasting_metrics


def generate_dynamic_kpis(df):
    """Executes all KPI modules dynamically and returns a list of dictionaries."""
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
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced finance KPIs.*"

    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_finance_analysis(payload, clients, df):
    # 1. Generate KPIs locally
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    # 2. Define Paths
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    # 3. Hand off to the Master Orchestrator
    return run_master_orchestrator(
        industry_name="finance",
        kpi_list=kpi_list,
        kpi_markdown=kpi_markdown,
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        sys_prompt_path=sys_prompt_path
    )
