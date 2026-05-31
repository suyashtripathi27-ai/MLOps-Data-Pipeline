"""
HR Industry Pipeline: Workforce Analytics & People Operations
Orchestrates all 8 HR KPI modules with governance filters for sensitive HR data.
"""
import os
from utils.master_orchestrator import run_master_orchestrator
from utils.kpi_engine import KPIEngine
from utils.prompt_engine import generate_v3_system_prompt
from .department_analysis import calc_department_metrics
from .workforce_stability_analysis import calc_workforce_stability_metrics
from .recruitment_analysis import calc_recruitment_metrics
from .productivity_analysis import calc_productivity_metrics
from .absenteeism_analysis import calc_absenteeism_metrics
from .engagement_analysis import calc_engagement_metrics
from .training_analysis import calc_training_metrics
from .compensation_analysis import calc_compensation_metrics
from .compliance_analysis import calc_compliance_metrics


def generate_dynamic_kpis(df):
    """
    Executes all HR KPI modules dynamically and returns a list of dictionaries.
    GOVERNANCE: Modules are ordered by priority (critical → supportive)
    """
    all_kpis = []
    
    # HIGH PRIORITY: Organizational continuity & staffing risk
    hr_modules = [
        ("Department Analysis", calc_department_metrics),  # 👈 INJECTED HERE (Establishes baseline headcount)
        ("Workforce Stability", calc_workforce_stability_metrics),
        ("Recruitment", calc_recruitment_metrics),
        ("Productivity", calc_productivity_metrics),
        ("Absenteeism", calc_absenteeism_metrics),
        # MEDIUM PRIORITY: Employee development & engagement
        ("Engagement", calc_engagement_metrics),
        ("Training", calc_training_metrics),
        # SENSITIVE: Compensation & Compliance require governance filters
        ("Compensation", calc_compensation_metrics),
        ("Compliance", calc_compliance_metrics),
    ]
    
    for module_name, module_func in hr_modules:
        try:
            kpis = module_func(df)
            all_kpis.extend(kpis)
        except Exception as e:
            print(f"⚠️ Warning: HR module {module_name} ({module_func.__name__}) failed: {e}")
    
    return all_kpis


def apply_hr_governance_filters(kpis):
    """
    CRITICAL HR GOVERNANCE:
    - Removes individual-level psychoanalysis
    - Removes protected attribute inferences
    - Keeps ONLY operational aggregated metrics
    - Applies sensitivity labels to compensation/compliance data
    """
    safe_kpis = []
    
    for kpi in kpis:
        # REJECT: Individual performance comparisons (no ranking)
        if any(term in kpi.get("name", "").lower() for term in ["ranked", "highest", "lowest performer", "individual rank"]):
            print(f"🚫 BLOCKED (HR Governance): {kpi.get('name', '')} - Individual ranking detected")
            continue
        
        # REJECT: Personality/mental health inferences
        if any(term in kpi.get("warnings", "").lower() for term in ["likely depressed", "personality", "mental health", "stress disorder", "psycho"]):
            print(f"🚫 BLOCKED (HR Governance): {kpi.get('name', '')} - Psychological inference detected")
            continue
        
        # REJECT: Discrimination/demographic profiling
        if any(term in kpi.get("category", "").lower() for term in ["by age", "by gender", "by race", "demographic pattern"]):
            print(f"🚫 BLOCKED (HR Governance): {kpi.get('name', '')} - Protected attribute inference detected")
            continue
        
        # ADD SENSITIVITY LABEL to compensation/compliance data
        if kpi.get("category", "") in ["💰 Compensation", "✅ Compliance", "⚠️ Risk"]:
            kpi["sensitivity"] = "HR_SENSITIVE"
            kpi["governance_note"] = "Operational metric only. Use in accordance with applicable employment laws."
        
        safe_kpis.append(kpi)
    
    return safe_kpis


def build_markdown_table(kpis):
    """Renders KPIs into a readable markdown table for the executive report."""
    if not kpis:
        return "*Insufficient HR data to generate insights.*"
    
    md = "| Category | KPI Name | Value | Formula | Source | Confidence | Warnings |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for k in kpis:
        sensitivity = f" [SENSITIVE]" if k.get("sensitivity") == "HR_SENSITIVE" else ""
        md += (
            f"| {k.get('category', '')} | "
            f"**{k.get('name', '')}{sensitivity}** | "
            f"`{k.get('value', '')}` | "
            f"*{k.get('formula', '')}* | "
            f"`{k.get('source', '')}` | "
            f"{k.get('confidence', 'N/A')} | "
            f"{k.get('warnings', 'None')} |\n"
        )
    
    return md


def run_hr_analysis(payload, clients, df):
    kpi_list = generate_dynamic_kpis(df)
    safe_kpis = apply_hr_governance_filters(kpi_list)
    final_kpis = KPIEngine.deduplicate_diagnostics(safe_kpis)
    kpi_markdown = build_markdown_table(final_kpis)
    system_prompt = generate_v3_system_prompt("hr")
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    
    return run_master_orchestrator(
        industry_name="hr",
        kpi_list=final_kpis,       
        kpi_markdown=kpi_markdown,  
        payload=payload,
        clients=clients,
        prompt_path=prompt_path,
        system_prompt_text=system_prompt
    )
