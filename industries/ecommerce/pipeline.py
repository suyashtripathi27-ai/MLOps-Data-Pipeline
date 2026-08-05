import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine
from utils.prompt_engine import generate_v3_system_prompt

from .cart_analysis import calc_cart_metrics
from .conversion_analysis import calc_conversion_metrics
from .customer_analysis import calc_customer_metrics
from .forecasting_analysis import calc_forecasting_metrics
from .fraud_analysis import calc_fraud_metrics
from .fulfillment_analysis import calc_fulfillment_metrics
from .inventory_analysis import calc_inventory_metrics
from .order_analysis import calc_order_metrics
from .pricing_analysis import calc_pricing_metrics
from .product_analysis import calc_product_metrics
from .promotion_analysis import calc_promotion_metrics
from .retention_analysis import calc_retention_metrics
from .review_analysis import calc_review_metrics
from .sales_analysis import calc_sales_metrics
from .traffic_analysis import calc_traffic_metrics
from utils.categorical_analysis import calc_universal_categorical_metrics # 👈 FIXED: Imported the universal module


def generate_dynamic_kpis(df):
    """Executes all KPI modules dynamically and returns a list of dictionaries."""
    all_kpis = []
    for module in [
        calc_sales_metrics,
        calc_customer_metrics,
        calc_conversion_metrics,
        calc_cart_metrics,
        calc_inventory_metrics,
        calc_order_metrics,
        calc_fulfillment_metrics,
        calc_pricing_metrics,
        calc_promotion_metrics,
        calc_traffic_metrics,
        calc_product_metrics,
        calc_review_metrics,
        calc_retention_metrics,
        calc_fraud_metrics,
        calc_forecasting_metrics,
        calc_universal_categorical_metrics # 👈 FIXED: Added to the execution loop
    ]:
        try:
            result = module(df)
            # 🛠️ FIXED: Added safety checks to prevent crashes if a module returns a dict instead of a list
            if isinstance(result, dict):
                all_kpis.append(result)
            elif isinstance(result, list):
                all_kpis.extend(result)
        except Exception as e:
            print(f"⚠️ Warning: E-commerce module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced ecommerce KPIs.*"

    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        if isinstance(k, dict): # 🛠️ FIXED: Added dictionary type check
            md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_ecommerce_analysis(payload, clients, df):
    raw_kpis = generate_dynamic_kpis(df)
    final_kpis = KPIEngine.deduplicate_diagnostics(raw_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    system_prompt = generate_v3_system_prompt("ecommerce")
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    
    return run_master_orchestrator(
        industry_name="ecommerce",
        kpi_list=final_kpis,
        kpi_markdown=kpi_markdown,
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        system_prompt_text=system_prompt
    )
