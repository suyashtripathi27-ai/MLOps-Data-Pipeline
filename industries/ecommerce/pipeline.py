import os
from utils.master_orchestrator import run_master_orchestrator

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

def generate_dynamic_kpis(df):
    all_kpis = []
    for module in [
        calc_sales_metrics, calc_customer_metrics, calc_conversion_metrics,
        calc_cart_metrics, calc_inventory_metrics, calc_order_metrics,
        calc_fulfillment_metrics, calc_pricing_metrics, calc_promotion_metrics,
        calc_traffic_metrics, calc_product_metrics, calc_review_metrics,
        calc_retention_metrics, calc_fraud_metrics, calc_forecasting_metrics,
    ]:
        try: all_kpis.extend(module(df))
        except Exception as e: print(f"⚠️ Warning: E-commerce module {module.__name__} failed: {e}")
    return all_kpis

def build_markdown_table(kpis):
    if not kpis: return "*Insufficient columns to generate advanced ecommerce KPIs.*"
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis: md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md

def run_ecommerce_analysis(payload, clients, df):
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    return run_master_orchestrator(
        industry_name="ecommerce",
        kpi_list=kpi_list, kpi_markdown=kpi_markdown,
        payload=payload, clients=clients,
        prompt_path=prompt_path, sys_prompt_path=sys_prompt_path
    )
