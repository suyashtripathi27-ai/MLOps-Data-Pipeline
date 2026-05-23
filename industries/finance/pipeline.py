from utils.insight_engine import synthesize_operational_signals
from utils.report_cleaner import clean_report_text
from utils.governance_engine import validate_operational_claims, inject_reliability_warning
import json
import os
from utils.llm_router import execute_with_fallback
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
    
    signals_dict = synthesize_operational_signals(kpi_list, industry="finance")
    
    narrative_blocks = signals_dict.get("PRIORITIZED_NARRATIVE_BLOCKS", {})
    top_3_clusters = dict(list(narrative_blocks.items())[:3])
    
    confidences = [data.get('aggregated_confidence', 1.0) for data in top_3_clusters.values()]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
    
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except: payload = {"raw_data": payload}
            
    payload['prioritized_signals'] = {"PRIORITIZED_NARRATIVE_BLOCKS": top_3_clusters}
    
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    sys_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        final_prompt = f.read().replace('{data_payload}', json.dumps(payload, indent=2))
        
    with open(sys_prompt_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    print("🧠 Consulting AI Finance Analyst...")
    try:
        raw_report = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
        
    clean_report = clean_report_text(raw_report)
    safe_report = validate_operational_claims(clean_report)
    final_report = inject_reliability_warning(safe_report, avg_confidence)
    
    return f"{final_report}\n\n---\n### 📊 Technical Appendix: Operational KPIs\n{kpi_markdown}"
