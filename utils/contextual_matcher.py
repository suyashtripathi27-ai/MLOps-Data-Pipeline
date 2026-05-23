import json
import os
import re
from functools import lru_cache

ONTOLOGY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ontology")

SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}

INDUSTRY_ROUTING_PATTERNS = {
    "ecommerce": {
        "keywords": ["checkout", "cart", "abandonment", "sku", "session", "aov", "rto", "retention"],
        "required_context": ["order", "customer", "conversion", "traffic"]
    },
    "retail": {
        "keywords": ["store", "dept", "weekly_sales", "footfall", "basket"],
        "required_context": ["sales", "inventory", "customer"]
    },
    "logistics": {
        "keywords": ["hub", "actual_time", "fleet", "osrm_time", "lane", "carrier"],
        "required_context": ["transit", "shipment", "route"]
    },
    "banking": {
        "keywords": ["account", "balance", "transaction", "loan", "deposit", "kyc"],
        "required_context": ["credit", "portfolio", "risk"]
    },
    "pharma": {
        "keywords": ["batch", "expiry", "purity", "therapeutic", "drug", "fda", "gmp"],
        "required_context": ["quality", "deviation", "sterility"]
    },
    "manufacturing": {
        "keywords": ["production", "manufacturing", "batch_id", "lot_number", "downtime", "defect_rate", "scrap"],
        "required_context": ["line", "plant", "inventory"]
    },
    "finance": {
        "keywords": ["revenue", "profit", "expense", "cashflow", "liquidity", "investment", "roi", "assets", "equity"],
        "required_context": ["margin", "ebitda", "working capital"]
    },
    "hr": {
        "keywords": ["employee", "attrition", "headcount", "absenteeism", "engagement"],
        "required_context": ["workforce", "retention", "talent"]
    }
}


def _json_load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_ontology_assets():
    return {
        "base": _json_load(os.path.join(ONTOLOGY_DIR, "base_ontology.json")),
        "governance": _json_load(os.path.join(ONTOLOGY_DIR, "governance_profiles.json")),
        "temporal": _json_load(os.path.join(ONTOLOGY_DIR, "temporal_extensions.json")),
        "polarity": _json_load(os.path.join(ONTOLOGY_DIR, "polarity_clusters.json")),
    }


def _contains(text, term):
    return term.lower() in text


def _infer_context_type(text):
    if any(token in text for token in ["employee", "attrition", "headcount", "workforce", "staff", "engagement"]):
        return "hr"
    if any(token in text for token in ["inventory", "stock", "sku", "warehouse", "wip", "fulfillment", "transit"]):
        return "inventory_management"
    return "financial"


def _build_cluster_catalog(industry):
    assets = _load_ontology_assets()
    base_clusters = assets["base"]["industries"].get(industry, {}).get("clusters", {})

    catalog = dict(base_clusters)
    for _, groups in assets["polarity"].items():
        for cluster_name, cluster_def in groups.items():
            applies_to = cluster_def.get("applies_to", ["*"])
            if "*" in applies_to or industry in applies_to:
                catalog.setdefault(cluster_name, cluster_def)

    return catalog


def _score_cluster(text, cluster_def, inferred_context):
    keywords = cluster_def.get("keywords", [])
    matched_keywords = [k for k in keywords if _contains(text, k)]
    if not matched_keywords:
        return None

    required_context = cluster_def.get("required_context", [])
    required_hits = [c for c in required_context if _contains(text, c)]
    if required_context and not required_hits:
        return None

    forbidden = cluster_def.get("forbidden_cooccurrence", [])
    forbidden_hits = [w for w in forbidden if _contains(text, w)]
    if forbidden_hits:
        return None

    score = len(matched_keywords) + (2 * len(required_hits))
    if cluster_def.get("context_type") == inferred_context:
        score += 2

    return {
        "score": score,
        "matched_keywords": matched_keywords,
        "required_context_hits": required_hits,
    }


def detect_industry_from_columns(columns_list):
    text = " ".join([str(c).lower() for c in columns_list])
    best = None

    for industry, pattern in INDUSTRY_ROUTING_PATTERNS.items():
        keyword_hits = [k for k in pattern.get("keywords", []) if _contains(text, k)]
        context_hits = [k for k in pattern.get("required_context", []) if _contains(text, k)]

        if not keyword_hits:
            continue

        score = len(keyword_hits) + (2 * len(context_hits))
        candidate = {
            "industry": industry,
            "score": score,
            "keyword_hits": keyword_hits,
            "context_hits": context_hits,
        }

        if best is None or candidate["score"] > best["score"]:
            best = candidate

    if not best:
        return None, {}

    return best["industry"], best


def detect_temporal_dynamics(text):
    assets = _load_ontology_assets()
    temporal = assets["temporal"]
    profile = temporal.get("default_temporal_profile", {})
    lower = text.lower()

    trajectory = "state"
    trajectory_direction = "stable"
    for direction, terms in temporal.get("trajectory_terms", {}).items():
        if any(_contains(lower, t) for t in terms):
            trajectory = "trajectory"
            trajectory_direction = direction
            break

    indicators = {}
    for indicator, buckets in temporal.get("trend_indicators", {}).items():
        selected = "baseline"
        for bucket, terms in buckets.items():
            if any(_contains(lower, t) for t in terms):
                selected = bucket
                break
        indicators[indicator] = selected

    return {
        "state_mode": trajectory,
        "trajectory_direction": trajectory_direction,
        "trend_indicators": indicators,
        "lookback_window": profile.get("lookback_window", "90d"),
        "baseline_comparison": profile.get("baseline_comparison", "trailing_4_period_average"),
    }


def apply_governance(industry, cluster_name, finding, severity):
    assets = _load_ontology_assets()
    profile = assets["governance"].get("profiles", {}).get(industry, {})
    clamp = profile.get("severity_clamping", {}).get(cluster_name)

    governance_applied = {
        "compliance_constraints": profile.get("compliance_constraints", []),
        "demographic_safety_checks": profile.get("demographic_safety_checks", []),
        "severity_clamped": False,
    }

    if not clamp:
        return finding, severity, governance_applied

    updated_finding = finding
    for forbidden_claim in clamp.get("forbidden_claims", []):
        pattern = re.compile(rf"\b{re.escape(forbidden_claim)}\b", flags=re.IGNORECASE)
        updated_finding = pattern.sub(clamp.get("replacement_claim", "anomaly_flagged"), updated_finding)

    max_severity = clamp.get("max_severity")
    updated_severity = severity
    if max_severity and SEVERITY_RANK.get(severity, 1) > SEVERITY_RANK.get(max_severity, 1):
        updated_severity = max_severity
        governance_applied["severity_clamped"] = True

    return updated_finding, updated_severity, governance_applied


def match_ontology_signal(category, name, warning="", industry="manufacturing"):
    text = f"{category} {name} {warning}".lower()
    inferred_context = _infer_context_type(text)
    catalog = _build_cluster_catalog(industry)

    best_name = None
    best_score = -1
    best_meta = {}
    best_def = None

    for cluster_name, cluster_def in catalog.items():
        scored = _score_cluster(text, cluster_def, inferred_context)
        if not scored:
            continue
        if scored["score"] > best_score:
            best_name = cluster_name
            best_score = scored["score"]
            best_meta = scored
            best_def = cluster_def

    if not best_def:
        return {
            "cluster": "general_operations_cluster",
            "impact_areas": ["general_monitoring"],
            "related_signals": [],
            "criticality": "internal_operational",
            "context_type": inferred_context,
            "hierarchy": {
                "subcluster": "general_operations",
                "signal_family": "monitoring",
                "specific_metric": "general_kpi"
            },
            "signal_weight": 0.5,
            "confidence_requirements": {"min_evidence": 1, "min_confidence": 0.5},
            "llm_reasoning_hints": "No strong ontology match found; monitor as baseline.",
            "match_debug": {"matched_keywords": [], "required_context_hits": []},
            "temporal_dynamics": detect_temporal_dynamics(text),
        }

    return {
        "cluster": best_name,
        "impact_areas": best_def.get("impact_areas", ["general_monitoring"]),
        "related_signals": best_def.get("related_signals", []),
        "criticality": best_def.get("criticality", "internal_operational"),
        "context_type": best_def.get("context_type", inferred_context),
        "hierarchy": best_def.get("hierarchy", {}),
        "signal_weight": best_def.get("signal_weight", 0.5),
        "confidence_requirements": best_def.get("confidence_requirements", {"min_evidence": 1, "min_confidence": 0.5}),
        "llm_reasoning_hints": best_def.get("llm_reasoning_hints", "Use conservative reasoning."),
        "match_debug": best_meta,
        "temporal_dynamics": detect_temporal_dynamics(text),
    }
