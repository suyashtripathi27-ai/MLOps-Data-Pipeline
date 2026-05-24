"""
INSIGHT ENGINE: Multi-Industry Operational Signal Synthesis
Routes KPIs to appropriate industry ontologies, detects signals, and prioritizes narratives.
Supports: Banking, Pharma, Manufacturing, Logistics, Retail, E-commerce, HR, Finance
"""
import hashlib
import re

# ==========================================
# LAYER 1: THE MASTER ONTOLOGY (Multi-Industry)
# ==========================================
INDUSTRY_ONTOLOGIES = {
    "banking": {
        "credit_risk_cluster": {
            "keywords": ["npl", "default", "delinquency", "charge off", "fico", "ltv", "arrears"],
            "impact_areas": ["capital_adequacy", "provision_expense", "asset_quality", "loss_reserve"],
            "related_signals": ["liquidity_risk_cluster"],
            "criticality": "customer_facing"
        },
        "aml_fraud_cluster": {
            "keywords": ["sar", "aml", "kyc", "fraud", "suspicious", "breach", "ctf"],
            "impact_areas": ["regulatory_fine", "reputational_damage", "license_risk"],
            "related_signals": [],
            "criticality": "customer_facing"
        },
        "liquidity_risk_cluster": {
            "keywords": ["cash", "liquidity", "reserve", "funding", "deposit", "withdrawal"],
            "impact_areas": ["solvency_risk", "operational_funding", "covenant_compliance"],
            "related_signals": ["credit_risk_cluster"],
            "criticality": "internal_operational"
        },
        "compliance_risk_cluster": {
            "keywords": ["audit", "compliance", "regulatory", "policy", "control", "deviation"],
            "impact_areas": ["regulatory_action", "fine", "enforcement"],
            "related_signals": ["aml_fraud_cluster"],
            "criticality": "customer_facing"
        }
    },
    
    "pharma": {
        "compliance_risk_cluster": {
            "keywords": ["fda", "audit", "gmp", "deviation", "sterility", "temperature", "excursion", "capa"],
            "impact_areas": ["regulatory_action", "batch_rejection", "market_recall", "product_hold"],
            "related_signals": ["quality_degradation_cluster"],
            "criticality": "customer_facing"
        },
        "quality_degradation_cluster": {
            "keywords": ["yield", "defect", "oos", "out_of_spec", "scrap", "purity", "potency"],
            "impact_areas": ["cost_of_goods", "supply_shortage", "batch_loss"],
            "related_signals": ["compliance_risk_cluster"],
            "criticality": "internal_operational"
        },
        "shelf_life_risk_cluster": {
            "keywords": ["expiry", "shelf_life", "stability", "expired", "near_expiry", "quarantine"],
            "impact_areas": ["inventory_loss", "product_destruction", "supply_disruption"],
            "related_signals": [],
            "criticality": "internal_operational"
        },
        "clinical_safety_cluster": {
            "keywords": ["adverse_event", "sae", "serious", "event_severity", "dropout", "safety_signal"],
            "impact_areas": ["market_suspension", "label_change", "liability_risk"],
            "related_signals": [],
            "criticality": "customer_facing"
        },
        "supply_chain_cluster": {
            "keywords": ["inventory", "procurement", "lead_time", "supplier", "logistics", "distribution"],
            "impact_areas": ["supply_shortage", "working_capital", "stockout_risk"],
            "related_signals": ["compliance_risk_cluster"],
            "criticality": "internal_operational"
        }
    },
    
    "manufacturing": {
        "production_instability_cluster": {
            "keywords": ["downtime", "maintenance", "oee", "efficiency", "utilization", "delay", "idle", "cycle_time"],
            "impact_areas": ["operational_efficiency", "throughput_risk", "capex_roi"],
            "related_signals": ["quality_degradation_cluster", "supply_chain_cluster"],
            "criticality": "internal_operational"
        },
        "quality_degradation_cluster": {
            "keywords": ["defect", "quality", "scrap", "reject", "fail", "oos", "yield", "rework"],
            "impact_areas": ["cost_of_poor_quality", "customer_satisfaction", "compliance_risk"],
            "related_signals": ["production_instability_cluster"],
            "criticality": "customer_facing"
        },
        "workforce_risk_cluster": {
            "keywords": ["safety", "incident", "accident", "turnover", "absenteeism", "labor", "overtime"],
            "impact_areas": ["regulatory_compliance", "employee_safety", "liability_cost"],
            "related_signals": ["production_instability_cluster"],
            "criticality": "internal_operational"
        },
        "supply_chain_cluster": {
            "keywords": ["inventory", "stock", "wip", "turnover", "lead_time", "freight", "transit", "procurement"],
            "impact_areas": ["working_capital", "stockout_risk", "holding_costs"],
            "related_signals": ["financial_performance_cluster"],
            "criticality": "internal_operational"
        },
        "financial_performance_cluster": {
            "keywords": ["sales", "revenue", "profit", "cost", "margin", "expense", "roi", "cogs"],
            "impact_areas": ["margin_erosion", "revenue_growth", "ebitda_impact"],
            "related_signals": ["supply_chain_cluster", "production_instability_cluster"],
            "criticality": "internal_operational"
        }
    },
    
    "logistics": {
        "network_bottleneck_cluster": {
            "keywords": ["transit_time", "delay", "detention", "demurrage", "port", "routing", "hub", "congestion"],
            "impact_areas": ["sla_breach", "customer_churn", "asset_utilization"],
            "related_signals": ["freight_cost_cluster"],
            "criticality": "customer_facing"
        },
        "freight_cost_cluster": {
            "keywords": ["fuel", "spot_rate", "carrier", "lane_cost", "accessorial", "cost", "margin"],
            "impact_areas": ["margin_erosion", "contract_profitability"],
            "related_signals": ["network_bottleneck_cluster"],
            "criticality": "internal_operational"
        },
        "cold_chain_cluster": {
            "keywords": ["temperature", "thermal_exposure", "cold_chain", "shelf_life", "excursion", "iot"],
            "impact_areas": ["product_loss", "quality_risk", "compliance_breach"],
            "related_signals": [],
            "criticality": "customer_facing"
        },
        "fleet_performance_cluster": {
            "keywords": ["fleet", "vehicle", "utilization", "mtbf", "mttr", "maintenance", "downtime"],
            "impact_areas": ["operational_efficiency", "maintenance_cost"],
            "related_signals": ["network_bottleneck_cluster"],
            "criticality": "internal_operational"
        }
    },
    
    "retail": {
        "store_performance_cluster": {
            "keywords": ["footfall", "conversion", "basket", "transaction", "shrinkage", "theft", "department"],
            "impact_areas": ["store_profitability", "comp_sales", "inventory_loss"],
            "related_signals": ["inventory_health_cluster"],
            "criticality": "customer_facing"
        },
        "inventory_health_cluster": {
            "keywords": ["stockout", "overstock", "turnover", "markdown", "clearance", "dead_stock", "sell_through"],
            "impact_areas": ["working_capital", "margin_erosion", "lost_sales"],
            "related_signals": ["store_performance_cluster"],
            "criticality": "internal_operational"
        },
        "customer_engagement_cluster": {
            "keywords": ["customer", "retention", "repeat", "clv", "satisfaction", "basket_size", "loyalty"],
            "impact_areas": ["customer_lifetime_value", "churn_risk", "revenue_growth"],
            "related_signals": ["store_performance_cluster"],
            "criticality": "customer_facing"
        },
        "pricing_promotion_cluster": {
            "keywords": ["price", "discount", "promotion", "margin", "elasticity", "roi", "uplift"],
            "impact_areas": ["margin_impact", "volume_tradeoff", "profitability"],
            "related_signals": ["store_performance_cluster"],
            "criticality": "internal_operational"
        }
    },
    
    "ecommerce": {
        "fulfillment_risk_cluster": {
            "keywords": ["delivery", "shipping", "delay", "fulfillment", "transit", "sla", "dso"],
            "impact_areas": ["customer_satisfaction", "sla_breach", "logistics_cost"],
            "related_signals": ["inventory_health_cluster"],
            "criticality": "customer_facing"
        },
        "inventory_health_cluster": {
            "keywords": ["stock", "stockout", "turnover", "overstock", "sku", "sell_through", "days_inventory"],
            "impact_areas": ["working_capital", "lost_sales", "carrying_cost"],
            "related_signals": ["fulfillment_risk_cluster"],
            "criticality": "internal_operational"
        },
        "customer_experience_cluster": {
            "keywords": ["checkout", "time_on_site", "conversion", "bounce", "cart", "retention", "clv"],
            "impact_areas": ["conversion_rate", "cart_abandonment", "customer_churn"],
            "related_signals": ["fulfillment_risk_cluster"],
            "criticality": "customer_facing"
        },
        "pricing_strategy_cluster": {
            "keywords": ["price", "discount", "margin", "elasticity", "revenue", "cost", "profit"],
            "impact_areas": ["revenue_optimization", "margin_protection"],
            "related_signals": ["fulfillment_risk_cluster"],
            "criticality": "internal_operational"
        }
    },
    
    "hr": {
        "workforce_stability_cluster": {
            "keywords": ["turnover", "attrition", "retention", "tenure", "exit", "voluntary", "involuntary"],
            "impact_areas": ["talent_drain", "recruiting_costs", "continuity_risk", "knowledge_loss"],
            "related_signals": ["recruitment_instability_cluster", "engagement_decline_cluster"],
            "criticality": "internal_operational"
        },
        "recruitment_instability_cluster": {
            "keywords": ["time_to_hire", "vacancy", "fill_rate", "offer_acceptance", "candidate", "pipeline"],
            "impact_areas": ["staffing_delay", "capacity_risk", "operational_understaffing"],
            "related_signals": ["workforce_stability_cluster", "productivity_pressure_cluster"],
            "criticality": "internal_operational"
        },
        "productivity_pressure_cluster": {
            "keywords": ["revenue_per_employee", "output", "utilization", "overtime", "workload", "efficiency"],
            "impact_areas": ["operational_efficiency", "burnout_risk", "performance_variability"],
            "related_signals": ["engagement_decline_cluster", "absenteeism_cluster"],
            "criticality": "internal_operational"
        },
        "engagement_decline_cluster": {
            "keywords": ["engagement", "satisfaction", "enps", "survey", "culture", "morale"],
            "impact_areas": ["retention_risk", "productivity_decline", "morale_instability"],
            "related_signals": ["workforce_stability_cluster", "absenteeism_cluster"],
            "criticality": "internal_operational"
        },
        "capability_gap_cluster": {
            "keywords": ["training", "completion", "certification", "skill_gap", "learning", "hours"],
            "impact_areas": ["skill_shortage", "operational_readiness", "future_workforce_risk"],
            "related_signals": ["productivity_pressure_cluster"],
            "criticality": "internal_operational"
        },
        "absenteeism_cluster": {
            "keywords": ["absence", "attendance", "unplanned_leave", "sick_leave", "no_show", "frequency"],
            "impact_areas": ["staffing_risk", "productivity_variability", "operational_disruption"],
            "related_signals": ["engagement_decline_cluster", "productivity_pressure_cluster"],
            "criticality": "internal_operational"
        },
        "compensation_pressure_cluster": {
            "keywords": ["salary", "overtime_cost", "benefits", "payroll", "compensation", "cost"],
            "impact_areas": ["payroll_pressure", "cost_control", "market_competitiveness"],
            "related_signals": ["workforce_stability_cluster"],
            "criticality": "internal_operational"
        },
        "workforce_compliance_cluster": {
            "keywords": ["policy", "compliance", "training", "incident", "harassment", "safety", "audit"],
            "impact_areas": ["regulatory_compliance", "organizational_risk", "liability_exposure"],
            "related_signals": [],
            "criticality": "customer_facing"
        }
    }
}

# ==========================================
# LAYER 2: SIGNAL ENRICHMENT ENGINE
# ==========================================
def map_to_ontology(category, name, industry="manufacturing"):
    """
    Maps KPI to appropriate industry ontology cluster.
    Falls back to manufacturing if industry not found.
    """
    text = f"{category} {name}".lower()
    
    # Safely fallback to manufacturing if the industry isn't found
    active_ontology = INDUSTRY_ONTOLOGIES.get(industry, INDUSTRY_ONTOLOGIES["manufacturing"])
    
    for cluster_name, rules in active_ontology.items():
        if any(keyword in text for keyword in rules["keywords"]):
            return cluster_name, rules["impact_areas"], rules["related_signals"], rules["criticality"]
    
    # Default fallback cluster
    return "general_operations_cluster", ["general_monitoring"], [], "internal_operational"


def calculate_numeric_confidence(label):
    """Converts confidence labels to numeric scores (0-1)."""
    mapping = {
        "🟢 High": 0.92,
        "High": 0.92,
        "🟡 Medium": 0.65,
        "Medium": 0.65,
        "🔴 Low": 0.35,
        "Low": 0.35
    }
    return mapping.get(label, 0.50)


def determine_operational_scope(name, category):
    """Determines if a KPI is systemic (organization-wide) or localized."""
    text = f"{category} {name}".lower()
    if any(k in text for k in ['total', 'overall', 'aggregate', 'average', 'mean', 'organization']):
        return "systemic"
    return "localized"


def clean_dimension_name(category):
    """Sanitizes category names for dimension keys."""
    return re.sub(r'[^\w\s]', '', category).strip().replace(' ', '_').lower()


def generate_signal(kpi, industry):
    """
    Converts a KPI into a structured signal with cluster mapping.
    This is where KPIs become operational insights.
    """
    warning = str(kpi.get("warnings", "None"))
    category = kpi.get("category", "General")
    name = kpi.get("name", "Metric")
    value = kpi.get("value", "")
    conf_label = kpi.get("confidence", "Medium")
    
    # Map KPI to industry ontology
    cluster, impacts, related, criticality = map_to_ontology(category, name, industry)
    
    signal = {
        "signal_id": hashlib.md5(f"{category}{name}".encode()).hexdigest()[:8],
        "cluster": cluster,
        "affected_dimension": clean_dimension_name(category),
        "business_area": category,
        "finding": f"{name} is at {value}",
        "raw_warning": warning,
        "impact_areas": impacts,
        "related_clusters": related,
        "business_criticality": criticality,
        "confidence_score": calculate_numeric_confidence(conf_label),
        "confidence_label": conf_label.replace("🟢 ", "").replace("🟡 ", "").replace("🔴 ", "").upper(),
        "operational_scope": determine_operational_scope(name, category)
    }
    
    # Determine severity based on warnings
    if warning != "None" and ("CRITICAL" in warning.upper() or "HIGH" in warning.upper() or ">" in warning or "BLOCKED" in warning.upper()):
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
    """
    Consolidates individual signals into cluster-level findings.
    Eliminates low-severity noise, groups by cluster.
    """
    consolidated = {}
    
    for sig in signals_list:
        # Skip LOW severity signals (noise reduction)
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
        
        # Build evidence chain
        consolidated[cluster]["evidence_chain"].append({
            "finding": sig["finding"],
            "evidence_strength": sig["evidence_strength"],
            "scope": sig["operational_scope"],
            "confidence": sig["confidence_score"]
        })
        
        consolidated[cluster]["raw_confidences"].append(sig["confidence_score"])
        consolidated[cluster]["unique_evidence_types"].add(sig["affected_dimension"])
        
        # Escalate if HIGH severity
        if sig["severity"] == "HIGH":
            consolidated[cluster]["highest_severity"] = "HIGH"
            consolidated[cluster]["time_sensitivity"] = "immediate_attention"
    
    return consolidated


def apply_cross_cluster_escalation(clusters, industry):
    """
    Applies industry-specific escalation rules.
    When multiple high-risk clusters appear, escalates to board-level urgency.
    """
    if industry == "manufacturing":
        # Manufacturing: Production + Quality = CRITICAL
        if "production_instability_cluster" in clusters and "quality_degradation_cluster" in clusters:
            clusters["production_instability_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["quality_degradation_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["production_instability_cluster"]["compounding_risk_detected"] = True
    
    elif industry == "pharma":
        # Pharma: Compliance + Quality = CRITICAL (regulatory risk)
        if "compliance_risk_cluster" in clusters and "quality_degradation_cluster" in clusters:
            clusters["compliance_risk_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["quality_degradation_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["compliance_risk_cluster"]["compounding_risk_detected"] = True
    
    elif industry == "logistics":
        # Logistics: Network Bottleneck + Cold Chain = CRITICAL
        if "network_bottleneck_cluster" in clusters and "cold_chain_cluster" in clusters:
            clusters["network_bottleneck_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["cold_chain_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
    
    elif industry == "ecommerce":
        # E-commerce: Fulfillment + Inventory = CRITICAL
        if "fulfillment_risk_cluster" in clusters and "inventory_health_cluster" in clusters:
            clusters["fulfillment_risk_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
    
    elif industry == "hr":
        # HR: Workforce Stability + Engagement = CRITICAL
        if "workforce_stability_cluster" in clusters and "engagement_decline_cluster" in clusters:
            clusters["workforce_stability_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["engagement_decline_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
    
    elif industry == "retail":
        # Retail: Store Performance + Inventory = CRITICAL
        if "store_performance_cluster" in clusters and "inventory_health_cluster" in clusters:
            clusters["store_performance_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
    
    elif industry == "banking":
        # Banking: Credit Risk + AML = CRITICAL
        if "credit_risk_cluster" in clusters and "aml_fraud_cluster" in clusters:
            clusters["credit_risk_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["aml_fraud_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
    
    return clusters


def calculate_priority_scores(clusters):
    """
    Calculates priority scores for each cluster.
    Weights by severity, criticality, confidence, and evidence diversity.
    """
    for cluster_name, data in clusters.items():
        # Calculate aggregated confidence
        avg_conf = sum(data["raw_confidences"]) / len(data["raw_confidences"]) if data["raw_confidences"] else 0
        data["aggregated_confidence"] = round(avg_conf, 2)
        
        # Evidence diversity score
        diversity_score = len(data["unique_evidence_types"])
        data["evidence_diversity_score"] = diversity_score
        
        # Severity weighting
        sev_weight = 3.0 if data["highest_severity"] == "HIGH" else 1.0
        if data["time_sensitivity"] == "CRITICAL_BOARD_LEVEL":
            sev_weight = 5.0
        
        # Business criticality weighting
        crit_weight = 1.5 if data["business_criticality"] == "customer_facing" else 1.0
        
        # Final priority score
        priority_score = (sev_weight * crit_weight) + avg_conf + (diversity_score * 0.5)
        data["cluster_priority_score"] = round(priority_score, 2)
        
        # Generate summary
        theme = cluster_name.replace('_cluster', '').replace('_', ' ')
        data["cluster_summary"] = (
            f"Detected {data['highest_severity']} priority indicators related to {theme} "
            f"across {len(data['evidence_chain'])} operational dimensions."
        )
        
        # Clean up temporary fields
        del data["raw_confidences"]
        del data["unique_evidence_types"]
    
    return clusters


def synthesize_operational_signals(kpi_list, industry="manufacturing"):
    """
    Main execution function: KPIs → Signals → Clusters → Narrative Blocks.
    
    Args:
        kpi_list: List of KPI dictionaries from analysis modules
        industry: Industry identifier for ontology selection
    
    Returns:
        Dictionary with PRIORITIZED_NARRATIVE_BLOCKS sorted by priority
    """
    # Step 1: Convert KPIs to signals with cluster mapping
    raw_signals = [generate_signal(kpi, industry) for kpi in kpi_list]
    
    # Step 2: Consolidate signals into clusters
    grouped_clusters = consolidate_signals(raw_signals)
    
    # Step 3: Apply industry-specific escalation rules
    escalated_clusters = apply_cross_cluster_escalation(grouped_clusters, industry)
    
    # Step 4: Calculate priority scores
    scored_clusters = calculate_priority_scores(escalated_clusters)
    
    # Step 5: Sort by priority
    sorted_narrative_blocks = dict(
        sorted(scored_clusters.items(), key=lambda item: item[1]['cluster_priority_score'], reverse=True)
    )
    
    return {"PRIORITIZED_NARRATIVE_BLOCKS": sorted_narrative_blocks}
