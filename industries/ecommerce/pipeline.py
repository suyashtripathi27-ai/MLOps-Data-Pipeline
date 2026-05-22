import json
import os

from utils.llm_router import execute_with_fallback
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
    try:
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
        ]:
            try:
                all_kpis.extend(module(df))
            except Exception as e:
                print(f"⚠️ Warning: Ecommerce module {module.__name__} failed: {e}")
        return all_kpis
    except Exception as e:
        print(f"⚠️ Warning: Ecommerce KPI generation failed: {e}")
        return []


def build_markdown_table(kpis):
    if not kpis:
        return "*Insufficient columns to generate advanced ecommerce KPIs.*"

    md_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in kpis:
        md_table += f"| {kpi.get('category', '')} | **{kpi.get('name', '')}** | `{kpi.get('value', '')}` | *{kpi.get('formula', '')}* | `{kpi.get('source', '')}` | {kpi.get('confidence', 'N/A')} | {kpi.get('warnings', 'None')} |\n"
    return md_table


def run_ecommerce_analysis(payload, clients, df):
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
    system_prompt = "You are an elite Ecommerce Analytics and Digital Commerce Strategy Consultant."

    print("🧠 Consulting AI Ecommerce Analyst...")
    try:
        report_content = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"

    return report_content.replace("{{INSERT_KPIS_HERE}}", kpi_markdown)
