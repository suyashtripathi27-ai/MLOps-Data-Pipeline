import hashlib
import re

from utils.contextual_matcher import apply_governance, match_ontology_signal


def map_to_ontology(category, name, warning="", industry="manufacturing"):
    """Context-aware ontology mapper with hierarchy, polarity balancing, and temporal hints."""
    return match_ontology_signal(category, name, warning=warning, industry=industry)


def calculate_numeric_confidence(label):
    mapping = {"🟢 High": 0.92, "High": 0.92, "🟡 Medium": 0.65, "Medium": 0.65, "🔴 Low": 0.35, "Low": 0.35}
    return mapping.get(label, 0.50)


def determine_operational_scope(name, category):
    text = f"{category} {name}".lower()
    if any(k in text for k in ["total", "overall", "revenue", "average"]):
        return "systemic"
    return "localized"


def clean_dimension_name(category):
    return re.sub(r"[^\w\s]", "", category).strip().replace(" ", "_").lower()


def generate_signal(kpi, industry):
    warning = str(kpi.get("warnings", "None"))
    category = kpi.get("category", "General")
    name = kpi.get("name", "Metric")
    value = kpi.get("value", "")
    conf_label = kpi.get("confidence", "Medium")

    ontology_match = map_to_ontology(category, name, warning=warning, industry=industry)

    signal = {
        "signal_id": hashlib.md5(f"{category}{name}".encode()).hexdigest()[:8],
        "cluster": ontology_match["cluster"],
        "subcluster": ontology_match["hierarchy"].get("subcluster", "general_operations"),
        "signal_family": ontology_match["hierarchy"].get("signal_family", "monitoring"),
        "specific_metric": ontology_match["hierarchy"].get("specific_metric", clean_dimension_name(name)),
        "affected_dimension": clean_dimension_name(category),
        "business_area": category,
        "finding": f"{name} is at {value}",
        "raw_warning": warning,
        "impact_areas": ontology_match["impact_areas"],
        "related_clusters": ontology_match["related_signals"],
        "business_criticality": ontology_match["criticality"],
        "context_type": ontology_match["context_type"],
        "signal_weight": ontology_match["signal_weight"],
        "confidence_requirements": ontology_match["confidence_requirements"],
        "llm_reasoning_hints": ontology_match["llm_reasoning_hints"],
        "temporal_dynamics": ontology_match["temporal_dynamics"],
        "match_debug": ontology_match["match_debug"],
        "confidence_score": calculate_numeric_confidence(conf_label),
        "confidence_label": conf_label.replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "").upper(),
        "operational_scope": determine_operational_scope(name, category),
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

    governed_finding, governed_severity, governance_meta = apply_governance(
        industry=industry,
        cluster_name=signal["cluster"],
        finding=signal["finding"],
        severity=signal["severity"],
    )
    signal["finding"] = governed_finding
    signal["severity"] = governed_severity
    signal["governance"] = governance_meta

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
                "subcluster": sig.get("subcluster"),
                "signal_family": sig.get("signal_family"),
                "specific_metric": sig.get("specific_metric"),
                "temporal_dynamics": sig.get("temporal_dynamics", {}),
                "governance": sig.get("governance", {}),
                "evidence_chain": [],
                "raw_confidences": [],
                "unique_evidence_types": set(),
            }

        consolidated[cluster]["evidence_chain"].append(
            {
                "finding": sig["finding"],
                "evidence_strength": sig["evidence_strength"],
                "scope": sig["operational_scope"],
                "confidence": sig["confidence_score"],
            }
        )

        consolidated[cluster]["raw_confidences"].append(sig["confidence_score"])
        consolidated[cluster]["unique_evidence_types"].add(sig["affected_dimension"])

        if sig["severity"] == "HIGH":
            consolidated[cluster]["highest_severity"] = "HIGH"
            consolidated[cluster]["time_sensitivity"] = "immediate_attention"

    return consolidated


def apply_cross_cluster_escalation(clusters, industry):
    # Industry-specific escalation rules
    if industry == "manufacturing":
        if "production_instability_cluster" in clusters and "quality_degradation_cluster" in clusters:
            clusters["production_instability_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["quality_degradation_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["production_instability_cluster"]["compounding_risk_detected"] = True

    elif industry == "ecommerce":
        if "fulfillment_instability_cluster" in clusters and "conversion_friction_cluster" in clusters:
            clusters["fulfillment_instability_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"

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

        theme = cluster_name.replace("_cluster", "").replace("_", " ")
        data["cluster_summary"] = (
            f"Detected {data['highest_severity']} priority indicators related to {theme} "
            f"across {len(data['evidence_chain'])} operational dimensions."
        )

        del data["raw_confidences"]
        del data["unique_evidence_types"]

    return clusters


def synthesize_operational_signals(kpi_list, industry="manufacturing"):
    """Main execution function, now accepts an industry parameter."""
    raw_signals = [generate_signal(kpi, industry) for kpi in kpi_list]

    grouped_clusters = consolidate_signals(raw_signals)
    escalated_clusters = apply_cross_cluster_escalation(grouped_clusters, industry)
    scored_clusters = calculate_priority_scores(escalated_clusters)

    sorted_narrative_blocks = dict(
        sorted(scored_clusters.items(), key=lambda item: item[1]["cluster_priority_score"], reverse=True)
    )

    return {"PRIORITIZED_NARRATIVE_BLOCKS": sorted_narrative_blocks}
