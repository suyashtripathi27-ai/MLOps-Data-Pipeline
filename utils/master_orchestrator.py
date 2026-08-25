import json
import os
from utils.insight_engine import synthesize_operational_signals
from utils.report_cleaner import clean_report_text
from utils.governance_engine import validate_operational_claims, inject_reliability_warning
from utils.llm_router import execute_with_fallback

# 🛠️ FIXED: Changed 'sys_prompt_path' to 'system_prompt_text=None'
def run_master_orchestrator(industry_name, kpi_list, kpi_markdown, payload, clients, prompt_path, system_prompt_text=None):
    """
    UNIVERSAL INTELLIGENCE ORCHESTRATOR
    Handles signal prioritization, LLM generation, and governance for all industries.
    """
    # 1. Extract and Prioritize Signals
    # Safely handle the payload first so its reliability data is available below
    if isinstance(payload, str):
        try: 
            payload = json.loads(payload)
        except: 
            payload = {"raw_data": payload}

    signals_dict = synthesize_operational_signals(
        kpi_list,
        industry=industry_name,
        data_reliability_score=payload.get("data_reliability_score"),
        system_warnings=payload.get("system_warnings")
    )
    
    # 🔥 TOP CLUSTER FILTERING
    # 🛠️ FIXED: insight_engine.py returns "OPERATIONAL_INTELLIGENCE", not
    # "PRIORITIZED_NARRATIVE_BLOCKS" — the old key never matched anything, so
    # top_3_clusters (and every confidence score derived from it) was always empty.
    narrative_blocks = signals_dict.get("OPERATIONAL_INTELLIGENCE", {})
    top_3_clusters = dict(list(narrative_blocks.items())[:3])
    
    # Calculate average confidence for governance later
    confidences = [data.get('aggregated_confidence', 1.0) for data in top_3_clusters.values()]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0
            
    # Send the top 3 prioritized clusters, plus the real governance signals
    # (excluded/missing metrics + data-integrity sanity flags) that
    # insight_engine.py already computed.
    payload['prioritized_signals'] = {
        "PRIORITIZED_NARRATIVE_BLOCKS": top_3_clusters,
        "GOVERNANCE_INTELLIGENCE": signals_dict.get("GOVERNANCE_INTELLIGENCE", [])
    }
    
    # 2. Load Prompts
    if not os.path.exists(prompt_path):
        return f"⚠️ Warning: prompt.txt missing.\n\n{kpi_markdown}"
        
    with open(prompt_path, 'r', encoding='utf-8') as f:
        final_prompt = f.read().replace('{data_payload}', json.dumps(payload, indent=2))
        
    # 🛠️ FIXED: We now use the injected V3 string directly instead of reading a file!
    if system_prompt_text:
        system_prompt = system_prompt_text
    else:
        system_prompt = "You are a Senior Enterprise Strategy Consultant."
        
    # 3. Generate AI Report
    print(f"🧠 Synthesizing {industry_name.capitalize()} Executive Intelligence...")
    try:
        raw_report = execute_with_fallback(clients, system_prompt, final_prompt)
    except Exception as e:
        return f"❌ CRITICAL API ERROR: {str(e)}\n\n### Backup Data Table\n{kpi_markdown}"
        
    # 4. POST-PROCESSING: Governance & Readability Cleaners
    clean_report = clean_report_text(raw_report)
    safe_report = validate_operational_claims(clean_report)
    final_report = inject_reliability_warning(safe_report, avg_confidence)
    
    # 5. FINAL ASSEMBLY
    # The kpi_markdown passed here is already clean and deduplicated from main.py
    return f"{final_report}\n\n---\n### 📊 Technical Appendix: Operational KPIs\n{kpi_markdown}"
