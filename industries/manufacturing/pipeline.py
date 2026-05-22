import os
import json
from .kpis import generate_manufacturing_kpis
from .reliability import run_manufacturing_governance_checks
from .charts import generate_manufacturing_charts


def build_markdown_table(kpis):
    """Formats KPI dictionaries into a traceable markdown table."""
    if not kpis:
        return "*Insufficient columns to generate advanced manufacturing KPIs.*"

    md_table = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md_table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    for kpi in kpis:
        md_table += (
            f"| {kpi.get('category', '')} | **{kpi.get('name', '')}** | `{kpi.get('value', '')}` | "
            f"*{kpi.get('formula', '')}* | `{kpi.get('source', '')}` | {kpi.get('confidence', 'N/A')} | "
            f"{kpi.get('warnings', 'None')} |\n"
        )
    return md_table


def run_manufacturing_analysis(payload, client, df):
    """Main orchestrator for the manufacturing analytics module."""
    kpi_list = generate_manufacturing_kpis(df)
    kpi_markdown = build_markdown_table(kpi_list)
    governance_warnings = run_manufacturing_governance_checks(df)
    generate_manufacturing_charts(df)

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"raw_data": payload}

    payload["kpi_results"] = kpi_list
    payload["manufacturing_governance_warnings"] = governance_warnings

    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
    if not os.path.exists(prompt_path):
        return "❌ ERROR: `prompt.txt` file missing from industries/manufacturing/ directory."

    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    if not prompt_template.strip():
        return "❌ ERROR: `prompt.txt` is completely empty."

    final_prompt = prompt_template.replace("{data_payload}", json.dumps(payload, indent=2))

    print("🧠 Consulting AI Manufacturing Analyst...")
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": "You are a pragmatic manufacturing analytics consultant. Focus only on the provided data context.",
                },
                {"role": "user", "content": final_prompt},
            ],
            temperature=0.2,
        )
        report_content = response.choices[0].message.content

        if not report_content:
            print("⚠️ API returned an empty response!")
            return "❌ API ERROR: Gemini returned a blank response."
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return f"❌ CRITICAL API ERROR: {str(e)}"

    if "{{INSERT_KPIS_HERE}}" in report_content:
        return report_content.replace("{{INSERT_KPIS_HERE}}", kpi_markdown)
    if "{INSERT_KPIS_HERE}" in report_content:
        return report_content.replace("{INSERT_KPIS_HERE}", kpi_markdown)
    return report_content + "\n\n### Traceable KPIs\n" + kpi_markdown
