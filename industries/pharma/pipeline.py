"""
Pharma Industry Analytics Pipeline
"""
import os
import json
from .kpis import generate_pharma_kpis
from .reliability import run_pharma_governance_checks

def generate_dynamic_kpis(df):
    """Executes all pharma KPI modules dynamically."""
    return generate_pharma_kpis(df)

def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced pharma KPIs.*"
        
    md_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in kpis:
        md_table += f"| {kpi.get('category', '')} | **{kpi.get('name', '')}** | `{kpi.get('value', '')}` | *{kpi.get('formula', '')}* | `{kpi.get('source', '')}` | {kpi.get('confidence', 'N/A')} | {kpi.get('warnings', 'None')} |\n"
    return md_table

def run_pharma_analysis(payload, client, df):
    """Main orchestrator for the pharma analytics module."""
    
    kpi_list = generate_dynamic_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    governance_warnings = run_pharma_governance_checks(df)

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"raw_data": payload}

    payload['kpi_results'] = kpi_list
    payload['pharma_governance_warnings'] = governance_warnings

    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    
    if not os.path.exists(prompt_path):
        return "❌ ERROR: `prompt.txt` file missing from industries/pharma/ directory."
        
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
        
    if not prompt_template.strip():
        return "❌ ERROR: `prompt.txt` is completely empty."
        
    final_prompt = prompt_template.replace('{data_payload}', json.dumps(payload, indent=2))
    
    print("🧬 Requesting Pharma-Specific AI Analysis...")
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": final_prompt}],
            temperature=0.3
        )
        ai_analysis = response.choices[0].message.content
    except Exception as e:
        ai_analysis = f"⚠️ AI analysis failed: {str(e)}"
    
    # Build comprehensive report
    final_report = f"""
# 💊 Pharmaceutical Industry Analysis Report

## 📊 KPI Metrics

{kpi_markdown}

## 🏥 Governance & Compliance

{chr(10).join(governance_warnings)}

## 🤖 AI-Powered Strategic Insights

{ai_analysis}

---
*Report Generated: Pharma Analytics Pipeline v1.0*
"""
    
    return final_report
