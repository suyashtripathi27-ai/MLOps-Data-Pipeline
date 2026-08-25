import hashlib
import re

# ==========================================
# LAYER 1: THE MASTER ONTOLOGY (Multi-Industry + Future State)
# ==========================================
INDUSTRY_ONTOLOGIES = {
    "manufacturing": {
        "production_instability_cluster": {
            "keywords": ["downtime", "maintenance", "oee", "efficiency", "utilization", "delay", "idle", "cycle time", "takt time", "bottleneck", "changeover", "breakdown", "mtbf", "mttr", "spindle time"],
            "impact_areas": ["operational_efficiency", "throughput_risk", "capex_roi", "capacity_constraints"],
            "related_signals": ["quality_degradation_cluster", "supply_chain_cluster"],
            "criticality": "internal_operational"
        },
        "quality_degradation_cluster": {
            "keywords": ["defect", "quality", "scrap", "reject", "fail", "oos", "purity", "rework", "first pass yield", "rft", "variance", "six sigma", "tolerance", "calibration", "warranty claim"],
            "impact_areas": ["cost_of_poor_quality", "customer_satisfaction", "compliance_risk", "brand_reputation"],
            "related_signals": ["production_instability_cluster"],
            "criticality": "customer_facing"
        },
        "workforce_risk_cluster": {
            "keywords": ["safety", "incident", "accident", "turnover", "absenteeism", "labor", "osha", "near miss", "ergonomics", "fatigue", "union", "strike", "grievance", "training matrix"],
            "impact_areas": ["regulatory_compliance", "employee_safety", "liability_cost", "production_continuity"],
            "related_signals": ["production_instability_cluster"],
            "criticality": "internal_operational"
        },
        "supply_chain_cluster": {
            "keywords": ["inventory", "stock", "wip", "turnover", "lead_time", "freight", "transit", "raw materials", "vendor fill rate", "safety stock", "jit", "kanban", "stockout", "expedite", "bom"],
            "impact_areas": ["working_capital", "stockout_risk", "holding_costs", "production_stoppage"],
            "related_signals": ["financial_performance_cluster"],
            "criticality": "internal_operational"
        },
        "financial_performance_cluster": {
            "keywords": ["sales", "revenue", "profit", "cost", "margin", "expense", "roi", "cogs", "absorption", "overhead", "capex", "opex", "depreciation", "ebitda", "payback period"],
            "impact_areas": ["margin_erosion", "revenue_growth", "ebitda_impact", "shareholder_value"],
            "related_signals": ["supply_chain_cluster", "production_instability_cluster"],
            "criticality": "internal_operational"
        },
        "environmental_sustainability_cluster": {
            "keywords": ["emissions", "carbon footprint", "waste", "effluent", "energy consumption", "kwh", "water usage", "esg", "recycling", "spill", "pollution", "hazardous"],
            "impact_areas": ["regulatory_fines", "public_relations", "sustainability_goals"],
            "related_signals": ["workforce_risk_cluster"],
            "criticality": "customer_facing"
        },
        "equipment_lifecycle_cluster": {
            "keywords": ["depreciation", "salvage value", "useful life", "commissioning", "decommissioning", "retrofitting", "asset lifecycle", "amortization"],
            "impact_areas": ["capital_planning", "asset_book_value", "tax_liability"],
            "related_signals": ["financial_performance_cluster"],
            "criticality": "internal_operational"
        }
    },
    "ecommerce": {
        "fulfillment_risk_cluster": {
            "keywords": ["delivery", "shipping", "delay", "fulfillment", "transit", "logistics", "last mile", "split shipment", "backorder", "pick pack", "dispatch", "carrier exception", "misroute"],
            "impact_areas": ["customer_satisfaction", "sla_breach", "logistics_cost", "nps_drop"],
            "related_signals": ["inventory_health_cluster", "returns_management_cluster"],
            "criticality": "customer_facing"
        },
        "inventory_health_cluster": {
            "keywords": ["stock", "stockout", "turnover", "overstock", "sku", "dead stock", "obsolete", "days of supply", "reorder point", "shrinkage", "allocations", "sell-through"],
            "impact_areas": ["working_capital", "lost_sales", "storage_fees", "markdown_risk"],
            "related_signals": ["fulfillment_risk_cluster"],
            "criticality": "internal_operational"
        },
        "customer_acquisition_cluster": {
            "keywords": ["cac", "cpa", "roas", "ctr", "cpc", "conversion rate", "bounce rate", "impression", "click-through", "funnel", "landing page", "affiliate", "retargeting"],
            "impact_areas": ["marketing_roi", "revenue_growth", "burn_rate"],
            "related_signals": ["platform_stability_cluster"],
            "criticality": "internal_operational"
        },
        "returns_management_cluster": {
            "keywords": ["rma", "return", "refund", "exchange", "reverse logistics", "restocking fee", "wardrobing", "damage", "salvage", "return rate"],
            "impact_areas": ["margin_erosion", "fraud_loss", "warehouse_congestion"],
            "related_signals": ["inventory_health_cluster", "fulfillment_risk_cluster"],
            "criticality": "internal_operational"
        },
        "platform_stability_cluster": {
            "keywords": ["uptime", "downtime", "latency", "load speed", "cart abandonment", "checkout error", "payment gateway", "api failure", "bug", "404", "session timeout"],
            "impact_areas": ["immediate_revenue_loss", "user_experience", "seo_ranking"],
            "related_signals": ["customer_acquisition_cluster"],
            "criticality": "customer_facing"
        }
    },
    "hr": {
        "retention_risk_cluster": {
            "keywords": ["turnover", "attrition", "flight risk", "resignation", "tenure", "voluntary leave", "exit interview", "poaching", "churn", "survival rate"],
            "impact_areas": ["talent_drain", "recruiting_costs", "continuity_risk", "institutional_knowledge_loss"],
            "related_signals": ["employee_engagement_cluster", "compensation_risk_cluster"],
            "criticality": "internal_operational"
        },
        "talent_acquisition_cluster": {
            "keywords": ["time to fill", "time to hire", "cost per hire", "applicant", "sourcing", "pipeline", "offer acceptance rate", "onboarding", "screening", "headcount"],
            "impact_areas": ["growth_bottlenecks", "recruitment_spend", "team_burnout"],
            "related_signals": ["retention_risk_cluster"],
            "criticality": "internal_operational"
        },
        "employee_engagement_cluster": {
            "keywords": ["enps", "satisfaction", "survey", "absenteeism", "burnout", "productivity", "morale", "presenteeism", "culture", "feedback", "wellbeing"],
            "impact_areas": ["productivity_loss", "culture_toxicity", "employer_brand"],
            "related_signals": ["retention_risk_cluster"],
            "criticality": "internal_operational"
        },
        "compliance_labor_cluster": {
            "keywords": ["fmla", "eeoc", "diversity", "inclusion", "grievance", "litigation", "harassment", "visa", "sponsorship", "flsa", "overtime violation", "workers comp"],
            "impact_areas": ["legal_liability", "reputational_damage", "regulatory_fines"],
            "related_signals": ["workforce_risk_cluster"],
            "criticality": "internal_operational"
        },
        "compensation_risk_cluster": {
            "keywords": ["pay gap", "equity", "bonus", "commission", "benefits", "market rate", "compa-ratio", "merit increase", "stock options", "vesting", "payroll"],
            "impact_areas": ["budget_overruns", "flight_risk", "internal_inequity"],
            "related_signals": ["retention_risk_cluster", "compliance_labor_cluster"],
            "criticality": "internal_operational"
        },
        "workforce_planning_cluster": {
            "keywords": ["succession planning", "skills gap", "bench strength", "span of control", "headcount forecast", "org design", "talent mapping"],
            "impact_areas": ["strategic_growth", "leadership_continuity", "restructuring_costs"],
            "related_signals": ["talent_acquisition_cluster"],
            "criticality": "internal_operational"
        }
    },
    "pharma": {
        "compliance_risk_cluster": {
            "keywords": ["fda", "audit", "gmp", "deviation", "sterility", "temperature", "excursion", "capa", "form 483", "warning letter", "sops", "validation", "pharmacovigilance"],
            "impact_areas": ["regulatory_action", "batch_rejection", "market_recall", "facility_shutdown"],
            "related_signals": ["quality_degradation_cluster", "supply_chain_integrity_cluster"],
            "criticality": "customer_facing"
        },
        "yield_degradation_cluster": {
            "keywords": ["yield", "titer", "batch", "loss", "scrap", "api", "fermentation", "purification", "assay", "potency", "impurity", "shelf life", "degradation"],
            "impact_areas": ["cost_of_goods", "supply_shortage", "margin_erosion"],
            "related_signals": ["compliance_risk_cluster"],
            "criticality": "internal_operational"
        },
        "clinical_trial_cluster": {
            "keywords": ["efficacy", "adverse event", "sae", "enrollment", "dropout", "placebo", "phase", "investigator", "protocol deviation", "data management", "endpoint", "blinded"],
            "impact_areas": ["time_to_market", "r_and_d_sunk_cost", "regulatory_approval_delay"],
            "related_signals": ["pipeline_risk_cluster"],
            "criticality": "internal_operational"
        },
        "supply_chain_integrity_cluster": {
            "keywords": ["cold chain", "serialization", "counterfeit", "traceability", "track and trace", "tamper", "dsicsa", "logistics", "temperature mapping", "ambient"],
            "impact_areas": ["patient_safety", "product_loss", "brand_damage"],
            "related_signals": ["compliance_risk_cluster"],
            "criticality": "customer_facing"
        },
        "pipeline_risk_cluster": {
            "keywords": ["patent cliff", "exclusivity", "formulation", "generic competition", "nda", "submission", "time to market", "orphan drug", "biosimilar"],
            "impact_areas": ["long_term_revenue", "market_share", "investor_confidence"],
            "related_signals": ["clinical_trial_cluster"],
            "criticality": "internal_operational"
        },
        "pharmacy_dispensing_cluster": {
            "keywords": ["otc", "rx", "prescription", "dispense", "pharmacy", "ndc_code", "pharmacist", "dosage", "co-pay", "claims"],
            "impact_areas": ["patient_adherence", "store_revenue", "inventory_turnover"],
            "related_signals": ["supply_chain_integrity_cluster"],
            "criticality": "customer_facing"
        },
        "market_access_cluster": {
            "keywords": ["formulary", "reimbursement", "payer", "pbm", "rebate", "copay card", "medicare", "medicaid", "pricing tier"],
            "impact_areas": ["drug_adoption", "gross_to_net_revenue", "market_penetration"],
            "related_signals": ["pipeline_risk_cluster"],
            "criticality": "customer_facing"
        }
    },
    "finance": {
        "liquidity_risk_cluster": {
            "keywords": ["cash flow", "working capital", "dscr", "burn rate", "runway", "receivables", "payables", "days sales outstanding", "dso", "dpo", "quick ratio", "current ratio", "solvency"],
            "impact_areas": ["solvency_risk", "operational_funding", "debt_covenant", "bankruptcy_risk"],
            "related_signals": ["margin_erosion_cluster", "credit_counterparty_cluster"],
            "criticality": "internal_operational"
        },
        "margin_erosion_cluster": {
            "keywords": ["ebitda", "gross margin", "cogs", "opex", "variance", "net income", "operating profit", "pricing pressure", "inflation", "cost overrun", "yield"],
            "impact_areas": ["profitability", "valuation", "dividend_risk"],
            "related_signals": ["liquidity_risk_cluster"],
            "criticality": "internal_operational"
        },
        "market_risk_cluster": {
            "keywords": ["interest rate", "fx", "forex", "volatility", "beta", "hedging", "derivatives", "commodity price", "swap", "exposure", "yield curve", "mark-to-market"],
            "impact_areas": ["portfolio_devaluation", "earnings_volatility", "capital_erosion"],
            "related_signals": ["liquidity_risk_cluster"],
            "criticality": "internal_operational"
        },
        "credit_counterparty_cluster": {
            "keywords": ["default", "credit rating", "downgrade", "exposure", "ar aging", "bad debt", "write-off", "provision", "collateral", "guarantor"],
            "impact_areas": ["revenue_loss", "cash_flow_interruption", "asset_impairment"],
            "related_signals": ["liquidity_risk_cluster"],
            "criticality": "internal_operational"
        },
        "capital_structure_cluster": {
            "keywords": ["leverage", "debt covenant", "equity dilution", "wacc", "cost of capital", "debt-to-equity", "gearing", "share buyback", "dividend yield", "issuance"],
            "impact_areas": ["borrowing_capacity", "shareholder_return", "control_dilution"],
            "related_signals": ["market_risk_cluster"],
            "criticality": "internal_operational"
        }
    },
    "banking": {
        "credit_risk_cluster": {
            "keywords": ["npl", "default", "delinquency", "charge off", "fico", "ltv", "dti", "provision", "forbearance", "collection", "recovery rate", "loss given default", "lgd", "pd"],
            "impact_areas": ["capital_adequacy", "provision_expense", "asset_quality", "profitability"],
            "related_signals": ["liquidity_risk_cluster", "deposit_concentration_cluster"],
            "criticality": "customer_facing"
        },
        "aml_fraud_cluster": {
            "keywords": ["sar", "aml", "kyc", "fraud", "suspicious", "breach", "sanctions", "pep", "structuring", "money laundering", "identity theft", "account takeover", "chargeback"],
            "impact_areas": ["regulatory_fine", "reputational_damage", "license_risk", "direct_financial_loss"],
            "related_signals": ["cybersecurity_risk_cluster"],
            "criticality": "customer_facing"
        },
        "customer_retention_cluster": {
            "keywords": ["churn", "attrition", "retention", "inactive", "one-time", "account closure", "balance transfer", "wallet share", "cross-sell", "up-sell"],
            "impact_areas": ["revenue_stability", "portfolio_growth", "customer_lifetime_value"],
            "related_signals": ["engagement_stability_cluster"],
            "criticality": "internal_operational"
        },
        "deposit_concentration_cluster": {
            "keywords": ["balance", "deposit", "concentration", "liquidity", "top 5%", "run on bank", "flight to quality", "hot money", "cd withdrawal", "funding gap"],
            "impact_areas": ["liquidity_risk", "funding_stability", "regulatory_intervention"],
            "related_signals": ["credit_risk_cluster", "interest_rate_risk_cluster"],
            "criticality": "internal_operational"
        },
        "engagement_stability_cluster": {
            "keywords": ["active_member", "credit_card", "usage", "engagement", "active accounts", "transactions per month", "app logins", "digital adoption", "feature usage"],
            "impact_areas": ["customer_loyalty", "cross_sell_potential", "fee_income"],
            "related_signals": ["customer_retention_cluster"],
            "criticality": "internal_operational"
        },
        "interest_rate_risk_cluster": {
            "keywords": ["alm", "nim", "net interest margin", "duration gap", "yield curve", "repricing", "rate hike", "spread", "basis risk"],
            "impact_areas": ["earnings_compression", "economic_value_of_equity"],
            "related_signals": ["deposit_concentration_cluster", "credit_risk_cluster"],
            "criticality": "internal_operational"
        },
        "cybersecurity_risk_cluster": {
            "keywords": ["data breach", "phishing", "ransomware", "ddos", "vulnerability", "patching", "unauthorized access", "malware", "encryption", "social engineering"],
            "impact_areas": ["system_outage", "data_loss", "massive_fines", "loss_of_trust"],
            "related_signals": ["aml_fraud_cluster"],
            "criticality": "customer_facing"
        }
    },
    "retail": {
        "store_performance_cluster": {
            "keywords": ["footfall", "conversion", "basket size", "upt", "shrinkage", "theft", "atv", "sales per square foot", "comp sales", "lfl", "dwell time", "pos"],
            "impact_areas": ["store_profitability", "comp_sales", "inventory_loss", "lease_roi"],
            "related_signals": ["inventory_health_cluster", "workforce_risk_cluster"],
            "criticality": "customer_facing"
        },
        "inventory_health_cluster": {
            "keywords": ["stockout", "overstock", "turnover", "markdown", "clearance", "gmroi", "sell-through", "weeks of supply", "planogram", "out of stock", "oos", "allocation"],
            "impact_areas": ["working_capital", "margin_erosion", "lost_sales"],
            "related_signals": ["store_performance_cluster", "merchandising_cluster"],
            "criticality": "internal_operational"
        },
        "omnichannel_integration_cluster": {
            "keywords": ["bopis", "ship from store", "click and collect", "endless aisle", "boris", "inventory visibility", "cross-channel", "unified commerce"],
            "impact_areas": ["customer_experience", "fulfillment_efficiency", "sales_attribution"],
            "related_signals": ["inventory_health_cluster"],
            "criticality": "customer_facing"
        },
        "merchandising_cluster": {
            "keywords": ["assortment", "elasticity", "pricing tier", "private label", "category management", "visual merchandising", "promotional lift", "cannibalization"],
            "impact_areas": ["gross_margin", "brand_positioning", "market_share"],
            "related_signals": ["inventory_health_cluster"],
            "criticality": "internal_operational"
        },
        "customer_loyalty_cluster": {
            "keywords": ["clv", "points", "churn", "reward redemption", "tier status", "loyalty program", "frequency", "recency", "rfm", "promoter"],
            "impact_areas": ["repeat_purchase_rate", "marketing_efficiency", "lifetime_value"],
            "related_signals": ["omnichannel_integration_cluster"],
            "criticality": "customer_facing"
        },
        "pricing_strategy_cluster": {
            "keywords": ["map pricing", "msrp", "dynamic pricing", "price matching", "price elasticity", "loss leader", "markup", "competitor pricing"],
            "impact_areas": ["gross_margin", "competitive_positioning", "sales_velocity"],
            "related_signals": ["merchandising_cluster"],
            "criticality": "internal_operational"
        }
    },
    "logistics": {
        "network_bottleneck_cluster": {
            "keywords": ["transit time", "delay", "detention", "demurrage", "port", "routing", "congestion", "dwell time", "hub", "sortation", "bottleneck", "capacity constraint", "rollover"],
            "impact_areas": ["sla_breach", "customer_churn", "asset_utilization", "penalty_fees"],
            "related_signals": ["freight_cost_cluster", "fleet_management_cluster"],
            "criticality": "customer_facing"
        },
        "freight_cost_cluster": {
            "keywords": ["fuel", "spot rate", "carrier", "lane cost", "accessorial", "toll", "tariff", "surcharge", "linehaul", "fsc", "cost per mile", "empty miles"],
            "impact_areas": ["margin_erosion", "contract_profitability", "pricing_competitiveness"],
            "related_signals": ["network_bottleneck_cluster"],
            "criticality": "internal_operational"
        },
        "fleet_management_cluster": {
            "keywords": ["telematics", "fuel efficiency", "idle time", "maintenance", "breakdown", "hours of service", "hos", "eld", "utilization", "deadhead", "depreciation", "driver shortage"],
            "impact_areas": ["capex_efficiency", "operating_costs", "safety_compliance"],
            "related_signals": ["network_bottleneck_cluster", "freight_cost_cluster"],
            "criticality": "internal_operational"
        },
        "last_mile_delivery_cluster": {
            "keywords": ["pod", "routing", "missed delivery", "density", "drop size", "residential fee", "signature", "attempted delivery", "geofencing", "time window"],
            "impact_areas": ["customer_satisfaction", "cost_to_serve", "driver_productivity"],
            "related_signals": ["network_bottleneck_cluster"],
            "criticality": "customer_facing"
        },
        "warehouse_operations_cluster": {
            "keywords": ["pick rate", "putaway", "cross-docking", "space utilization", "slotting", "shrinkage", "cycle count", "wms", "pallet", "forklift", "labor management"],
            "impact_areas": ["order_cycle_time", "storage_costs", "inventory_accuracy"],
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
