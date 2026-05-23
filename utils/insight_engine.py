import hashlib
import re

# ==========================================
# LAYER 1: THE ONTOLOGY (Configuration-Driven)
# ==========================================
CLUSTER_ONTOLOGY = {
    "production_instability_cluster": {
        "keywords": ["downtime", "maintenance", "oee", "efficiency", "utilization", "delay", "idle"],
        "impact_areas": ["operational_efficiency", "throughput_risk", "capex_roi"],
        "related_signals": ["quality_degradation_cluster", "supply_chain_cluster"],
        "criticality": "internal_operational"
    },
    "quality_degradation_cluster": {
        "keywords": ["defect", "quality", "scrap", "reject", "fail", "oos", "purity"],
        "impact_areas": ["cost_of_poor_quality", "customer_satisfaction", "compliance_risk"],
        "related_signals": ["production_instability_cluster"],
        "criticality": "customer_facing"
    },
    "workforce_risk_cluster": {
        "keywords": ["safety", "incident", "accident", "turnover", "absenteeism", "labor"],
        "impact_areas": ["regulatory_compliance", "employee_safety", "liability_cost"],
        "related_signals": ["production_instability_cluster"],
        "criticality": "internal_operational"
    },
    "supply_chain_cluster": {
        "keywords": ["inventory", "stock", "wip", "turnover", "lead_time", "freight", "transit"],
        "impact_areas": ["working_capital", "stockout_risk", "holding_costs"],
        "related_signals": ["financial_performance_cluster"],
        "criticality": "internal_operational"
    },
    "financial_performance_cluster": {
        "keywords": ["sales", "revenue", "profit", "cost", "margin", "expense", "roi"],
        "impact_areas": ["margin_erosion", "revenue_growth", "ebitda_impact"],
        "related_signals": ["supply_chain_cluster", "production_instability_cluster"],
        "criticality": "internal_operational"
    }
}

# ==========================================
# LAYER 2: SIGNAL ENRICHMENT ENGINE
# ==========================================
def map_to_ontology(category, name):
    text = f"{category} {name}".lower()
    for cluster_name, rules in CLUSTER_ONTOLOGY.items():
        if any(keyword in text for keyword in rules["keywords"]):
            return cluster_name, rules["impact_areas"], rules["related_signals"], rules["criticality"]
    return "general_operations_cluster", ["general_monitoring"], [], "internal_operational"

def calculate_numeric_confidence(label):
    mapping = {"🟢 High": 0.92, "High": 0.92, "🟡 Medium": 0.65, "Medium": 0.65, "🔴 Low": 0.35, "Low": 0.35}
    return mapping.get(label, 0.50)

def determine_operational_scope(name, category):
    text = f"{category} {name}".lower()
    if any(k in text for k in ['total', 'overall', 'revenue', 'average']):
        return "systemic"
    return "localized"

def clean_dimension_name(category):
    """Strips emojis and formatting to create a clean affected_dimension tag."""
    return re.sub(r'[^\w\s]', '', category).strip().replace(' ', '_').lower()

def generate_signal(kpi):
    warning = str(kpi.get("warnings", "None"))
    category = kpi.get("category", "General")
    name = kpi.get("name", "Metric")
    value = kpi.get("value", "")
    conf_label = kpi.get("confidence", "Medium")
    
    cluster, impacts, related, criticality = map_to_ontology(category, name)
    
    signal = {
        "signal_id": hashlib.md5(f"{category}{name}".encode()).hexdigest()[:8],
        "cluster": cluster,
        "affected_dimension": clean_dimension_name(category), # <-- ADJUSTMENT 3
        "business_area": category,
        "finding": f"{name} is at {value}",
        "raw_warning": warning,                               # <-- ADJUSTMENT 2
        "impact_areas": impacts,
        "related_clusters": related,
        "business_criticality": criticality,
        "confidence_score": calculate_numeric_confidence(conf_label),
        "confidence_label": conf_label.replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "").upper(),
        "operational_scope": determine_operational_scope(name, category)
    }
    
    if warning != "None" and ("CRITICAL" in warning.upper() or "HIGH" in warning.upper() or ">" in warning):
        signal["severity"] = "HIGH"
        signal["evidence_strength"] = "strong_statistical_outlier"
        signal["time_sensitivity"] = "immediate_attention"
    elif warning != "None":
        signal["severity"] = "MEDIUM"
        signal["evidence_strength"] = "moderate_variance"
        signal["time_sensitivity"] = "monitoring_required"
    else:
        signal["severity"] = "LOW"
        signal["evidence_strength"] = "baseline_normal"
        signal["time_sensitivity"] = "none"
        
    return signal

# ==========================================
# LAYER 3: DEDUPLICATION, WEIGHTING & ESCALATION
# ==========================================
def consolidate_signals(signals_list):
    consolidated = {}
    
    for sig in signals_list:
        if sig["severity"] == "LOW":
            continue 
            
        cluster = sig["cluster"]
        if cluster not in consolidated:
            consolidated[cluster] = {
                "business_criticality": sig["business_criticality"],
                "primary_impacts": sig["impact_areas"],
                "highest_severity": sig["severity"],
                "time_sensitivity": sig["time_sensitivity"],
                "evidence_chain": [],
                "raw_confidences": [],
                "unique_evidence_types": set()
            }
            
        consolidated[cluster]["evidence_chain"].append({
            "finding": sig["finding"],
            "evidence_strength": sig["evidence_strength"],
            "scope": sig["operational_scope"],
            "confidence": sig["confidence_score"]
        })
        
        consolidated[cluster]["raw_confidences"].append(sig["confidence_score"])
        consolidated[cluster]["unique_evidence_types"].add(sig["affected_dimension"])
        
        if sig["severity"] == "HIGH":
            consolidated[cluster]["highest_severity"] = "HIGH"
            consolidated[cluster]["time_sensitivity"] = "immediate_attention"

    return consolidated

def apply_cross_cluster_escalation(clusters):
    if "production_instability_cluster" in clusters and "quality_degradation_cluster" in clusters:
        clusters["production_instability_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
        clusters["quality_degradation_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
        clusters["production_instability_cluster"]["compounding_risk_detected"] = True
    return clusters

def calculate_priority_scores(clusters):
    for cluster_name, data in clusters.items():
        avg_conf = sum(data["raw_confidences"]) / len(data["raw_confidences"])
        data["aggregated_confidence"] = round(avg_conf, 2)
        
        diversity_score = len(data["unique_evidence_types"])
        data["evidence_diversity_score"] = diversity_score
        
        sev_weight = 3.0 if data["highest_severity"] == "HIGH" else 1.0
        if data["time_sensitivity"] == "CRITICAL_BOARD_LEVEL":
            sev_weight = 5.0
            
        crit_weight = 1.5 if data["business_criticality"] == "customer_facing" else 1.0
        
        priority_score = (sev_weight * crit_weight) + avg_conf + (diversity_score * 0.5)
        data["cluster_priority_score"] = round(priority_score, 2)
        
        # <-- ADJUSTMENT 1: Dynamic Narrative Summary
        theme = cluster_name.replace('_cluster', '').replace('_', ' ')
        data["cluster_summary"] = f"Detected {data['highest_severity']} priority indicators related to {theme} across {len(data['evidence_chain'])} operational dimensions."
        
        del data["raw_confidences"]
        del data["unique_evidence_types"]
        
    return clusters

def synthesize_operational_signals(kpi_list):
    raw_signals = [generate_signal(kpi) for kpi in kpi_list]
    
    grouped_clusters = consolidate_signals(raw_signals)
    escalated_clusters = apply_cross_cluster_escalation(grouped_clusters)
    scored_clusters = calculate_priority_scores(escalated_clusters)
    
    sorted_narrative_blocks = dict(
        sorted(scored_clusters.items(), key=lambda item: item[1]['cluster_priority_score'], reverse=True)
    )
    
    return {"PRIORITIZED_NARRATIVE_BLOCKS": sorted_narrative_blocks}
