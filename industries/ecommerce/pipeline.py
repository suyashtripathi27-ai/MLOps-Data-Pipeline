from utils.insight_engine import synthesize_operational_signals
from utils.report_cleaner import clean_report_text
from utils.governance_engine import validate_operational_claims, inject_reliability_warning
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
    """Run all E-commerce KPI modules and collect results."""
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
            print(f"⚠️ Warning: E-commerce module {module.__name__} failed: {e}")
    return all_kpis


def build_markdown_table(kpis):
    if not kpis:
        return "*Insufficient columns to generate advanced ecommerce KPIs.*"

    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for k in kpis:
        md += f"| {k.get('category','')} | **{k.get('name','')}** | `{k.get('value','')}` | *{k.get('formula','')}* | `{k.get('source','')}` | {k.get('confidence','N/A')} | {k.get('warnings','None')} |\n"
    return md


def run_ecommerce_analysis(payload, clients, df):
    # 1. Generate Raw Data
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    
    # 2. Extract and Prioritize Signals - FLIPPED TO ECOMMERCE
    signals_dict = synthesize_operational_signals(kpi_list, industry="ecommerce")
    
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
            
    # Send ONLY the top 3 clusters to keep AI focused
    payload['prioritized_signals'] = {"PRIORITIZED_N
