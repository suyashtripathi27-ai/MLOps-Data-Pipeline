import hashlib
import re

# ==========================================
# LAYER 1: THE MASTER ONTOLOGY (Multi-Industry + Future State)
# ==========================================
INDUSTRY_ONTOLOGIES = {
    "manufacturing": {
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
    },
    "ecommerce": {
        "fulfillment_risk_cluster": {
            "keywords": ["delivery", "shipping", "delay", "fulfillment", "transit", "logistics"],
            "impact_areas": ["customer_satisfaction", "sla_breach", "logistics_cost"],
            "related_signals": ["inventory_health_cluster"],
            "criticality": "customer_facing"
        },
        "inventory_health_cluster": {
            "keywords": ["stock", "stockout", "turnover", "overstock", "sku"],
            "impact_areas": ["working_capital", "lost_sales"],
            "related_signals": ["fulfillment_risk_cluster"],
            "criticality": "internal_operational"
        }
    },
    "hr": {
        "retention_risk_cluster": {
            "keywords": ["turnover", "attrition", "flight risk", "resignation", "tenure"],
            "impact_areas": ["talent_drain", "recruiting_costs", "continuity_risk"],
            "related_signals": ["employee_engagement_cluster"],
            "criticality": "internal_operational"
        }
    },
    "pharma": {
        "compliance_risk_cluster": {
            "keywords": ["fda", "audit", "gmp", "deviation", "sterility", "temperature", "excursion"],
            "impact_areas": ["regulatory_action", "batch_rejection", "market_recall"],
            "related_signals": ["quality_degradation_cluster"],
            "criticality": "customer_facing"
        },
        "yield_degradation_cluster": {
            "keywords": ["yield", "titer", "batch", "loss", "scrap", "api"],
            "impact_areas": ["cost_of_goods", "supply_shortage"],
            "related_signals": ["compliance_risk_cluster"],
            "criticality": "internal_operational"
        }
    },
    "finance": {
        "liquidity_risk_cluster": {
            "keywords": ["cash flow", "working capital", "dscr", "burn rate", "runway", "receivables"],
            "impact_areas": ["solvency_risk", "operational_funding", "debt_covenant"],
            "related_signals": ["margin_erosion_cluster"],
            "criticality": "internal_operational"
        },
        "margin_erosion_cluster": {
            "keywords": ["ebitda", "gross margin", "cogs", "opex", "variance"],
            "impact_areas": ["profitability", "valuation", "dividend_risk"],
            "related_signals": ["liquidity_risk_cluster"],
            "criticality": "internal_operational"
        }
    },
    "banking": {
        "credit_risk_cluster": {
            "keywords": ["npl", "default", "delinquency", "charge off", "fico", "ltv"],
            "impact_areas": ["capital_adequacy", "provision_expense", "asset_quality"],
            "related_signals": ["liquidity_risk_cluster"],
            "criticality": "customer_facing"
        },
        "aml_fraud_cluster": {
            "keywords": ["sar", "aml", "kyc", "fraud", "suspicious", "breach"],
            "impact_areas": ["regulatory_fine", "reputational_damage", "license_risk"],
            "related_signals": [],
            "criticality": "customer_facing"
        },
        "customer_retention_cluster": {
            "keywords": ["churn", "attrition", "retention", "inactive", "one-time"],
            "impact_areas": ["revenue_stability", "portfolio_growth", "customer_lifetime_value"],
            "related_signals": ["engagement_stability_cluster"],
            "criticality": "internal_operational"
        },
        "deposit_concentration_cluster": {
            "keywords": ["balance", "deposit", "concentration", "liquidity", "top 5%"],
            "impact_areas": ["liquidity_risk", "funding_stability"],
            "related_signals": ["credit_risk_cluster"],
            "criticality": "internal_operational"
        },
        "engagement_stability_cluster": {
            "keywords": ["active_member", "credit_card", "usage", "engagement", "active accounts"],
            "impact_areas": ["customer_loyalty", "cross_sell_potential"],
            "related_signals": ["customer_retention_cluster"],
            "criticality": "internal_operational"
        }
    },
    "retail": {
        "store_performance_cluster": {
            "keywords": ["footfall", "conversion", "basket size", "upt", "shrinkage", "theft"],
            "impact_areas": ["store_profitability", "comp_sales", "inventory_loss"],
            "related_signals": ["inventory_health_cluster"],
            "criticality": "customer_facing"
        },
        "inventory_health_cluster": {
            "keywords": ["stockout", "overstock", "turnover", "markdown", "clearance"],
            "impact_areas": ["working_capital", "margin_erosion"],
            "related_signals": ["store_performance_cluster"],
            "criticality": "internal_operational"
        }
    },
    "logistics": {
        "network_bottleneck_cluster": {
            "keywords": ["transit time", "delay", "detention", "demurrage", "port", "routing"],
            "impact_areas": ["sla_breach", "customer_churn", "asset_utilization"],
            "related_signals": ["freight_cost_cluster"],
            "criticality": "customer_facing"
        },
        "freight_cost_cluster": {
            "keywords": ["fuel", "spot rate", "carrier", "lane cost", "accessorial"],
            "impact_areas": ["margin_erosion", "contract_profitability"],
            "related_signals": ["network_bottleneck_cluster"],
            "criticality": "internal_operational"
        }
    }
}

# ==========================================
# LAYER 2: SIGNAL ENRICHMENT ENGINE
# ==========================================
def map_to_ontology(category, name, industry="manufacturing"):
    text = f"{category} {name}".lower()
    active_ontology = INDUSTRY_ONTOLOGIES.get(industry, INDUSTRY_ONTOLOGIES["manufacturing"])
    for cluster_name, rules in active_ontology.items():
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
    return re.sub(r'[^\w\s]', '', category).strip().replace(' ', '_').lower()

def generate_signal(kpi, industry):
    warning = str(kpi.get("warnings", "None"))
    category = kpi.get("category", "General")
    name = kpi.get("name", "Metric")
    value = kpi.get("value", "")
    conf_label = str(kpi.get("confidence", "Medium"))
    
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

def apply_cross_cluster_escalation(clusters, industry):
    if industry == "manufacturing":
        if "production_instability_cluster" in clusters and "quality_degradation_cluster" in clusters:
            clusters["production_instability_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["quality_degradation_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            clusters["production_instability_cluster"]["compounding_risk_detected"] = True
            
    elif industry == "ecommerce":
        if "fulfillment_risk_cluster" in clusters and "inventory_health_cluster" in clusters:
            clusters["fulfillment_risk_cluster"]["time_sensitivity"] = "CRITICAL_BOARD_LEVEL"
            
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
        
        theme = cluster_name.replace('_cluster', '').replace('_', ' ')
        data["cluster_summary"] = f"Detected {data['highest_severity']} priority indicators related to {theme} across {len(data['evidence_chain'])} operational dimensions."
        
        del data["raw_confidences"]
        del data["unique_evidence_types"]
        
    return clusters

# ==========================================
# LAYER 4: THE NEW SEPARATED SYNTHESIS PIPELINE
# ==========================================
def synthesize_operational_signals(kpi_list, industry="manufacturing"):
    """
    Separates operational intelligence from governance intelligence.
    Prevents missing data warnings from generating false positive risk clusters.
    """
    # 1. Split signals by explicit classification
    operational_kpis = [k for k in kpi_list if k.get("signal_type", "operational") != "governance"]
    governance_kpis = [k for k in kpi_list if k.get("signal_type") == "governance"]

    # 2. OPERATIONAL INTELLIGENCE (Full clustering & scoring)
    raw_signals = [generate_signal(kpi, industry) for kpi in operational_kpis]
    grouped_clusters = consolidate_signals(raw_signals)
    escalated_clusters = apply_cross_cluster_escalation(grouped_clusters, industry)
    scored_clusters = calculate_priority_scores(escalated_clusters)
    
    sorted_operational_blocks = dict(
        sorted(scored_clusters.items(), key=lambda item: item[1]['cluster_priority_score'], reverse=True)
    )

    # 3. GOVERNANCE INTELLIGENCE (Direct mapping, no clustering hallucination)
    governance_signals = []
    for k in governance_kpis:
        governance_signals.append({
            "severity": "LOW",
            "issue": k.get("warnings", "Data excluded by governance engine."),
            "affected_area": k.get("category", "System Diagnostics")
        })

    # 4. Strict return structure for LLM routing
    return {
        "OPERATIONAL_INTELLIGENCE": sorted_operational_blocks,
        "GOVERNANCE_INTELLIGENCE": governance_signals
    }
