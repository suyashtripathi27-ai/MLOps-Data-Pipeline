"""
GOVERNANCE ENGINE: Universal and Industry-Specific Content Filters
Ensures all AI-generated reports meet ethical, legal, and operational standards.
Supports: Banking, Pharma, Manufacturing, Logistics, Retail, E-commerce, HR, Finance
"""
import re


# ==========================================
# LAYER 1: UNIVERSAL GOVERNANCE FILTERS
# ==========================================

def validate_operational_claims(report):
    """
    UNIVERSAL CLAIM VALIDATOR: Downgrades absolute claims to probabilistic consulting language.
    Applies to all industries - removes causation overreach, converts to correlations.
    """
    prohibited_terms = {
        "caused by": "may be associated with",
        "definitely": "likely",
        "guarantees": "suggests a high probability of",
        "certainly due to": "potentially driven by",
        "proves that": "indicates that",
        "will result in": "could result in",
        "is already creating": "may be contributing to",
        "direct consequence": "potential consequence",
        "must": "should",
        "always": "often",
        "never": "rarely",
        "impossible": "unlikely"
    }
    
    for bad_word, safe_word in prohibited_terms.items():
        report = re.sub(rf'\b{bad_word}\b', safe_word, report, flags=re.IGNORECASE)
    
    return downgrade_theatrics(report)


def downgrade_theatrics(report):
    """
    UNIVERSAL THEATRICS DOWNGRADER: Strips alarmist adjectives.
    Converts emotional language to professional consulting tone.
    """
    theatrics = {
        r"\b(highly precarious)\b": "operationally sensitive",
        r"\b(profound breakdown)\b": "elevated operational instability",
        r"\b(profound)\b": "notable",
        r"\b(immediate, high-priority risk)\b": "primary operational risk",
        r"\b(catastrophic)\b": "severe",
        r"\b(alarming)\b": "notable",
        r"\b(massive)\b": "substantial",
        r"\b(stark reality)\b": "current operational baseline",
        r"\b(deeply entrenched)\b": "systemic",
        r"\b(critical vulnerability)\b": "operational vulnerability",
        r"\b(crisis)\b": "challenge",
        r"\b(pervasive)\b": "distributed",
        r"\b(devastating)\b": "significant",
        r"\b(unprecedented)\b": "notable",
        r"\b(disastrous)\b": "unfavorable",
        r"\b(severely impacted)\b": "substantially affected",
        r"\b(rapidly deteriorating)\b": "trending downward"
    }
    
    for pattern, safe_word in theatrics.items():
        report = re.sub(pattern, safe_word, report, flags=re.IGNORECASE)
    
    return report


def inject_reliability_warning(report, avg_confidence):
    """
    UNIVERSAL LIABILITY SHIELD: Injects confidence warnings when data quality is low.
    Protects organization from liability due to fragmented data.
    """
    if avg_confidence < 0.65:
        warning = (
            "\n> **⚠️ GOVERNANCE WARNING:** Several findings in this report rely on fragmented or low-confidence data. "
            "Interpret these signals cautiously and validate with additional telemetry before making operational decisions."
        )
        report = report.replace("# 1. Executive Situation Report", f"# 1. Executive Situation Report{warning}")
    
    return report


# ==========================================
# LAYER 2: INDUSTRY-SPECIFIC GOVERNANCE
# ==========================================

def validate_hr_claims(report):
    """
    HR-SPECIFIC GOVERNANCE FILTER
    Removes individual profiling, psychoanalysis, and discrimination inferences.
    
    CRITICAL: HR governance is the strictest because of employment law implications.
    """
    # Reject individual-level behavioral analysis
    individual_profiling_patterns = [
        r"\b(employee.*is likely.*\w+(ed|ing))\b",  # "employee is likely stressed"
        r"\b(person(al|ality|alistic).*profile)\b",
        r"\b(individual.*rank|ranking)\b",
        r"\b(behavioral.*pattern.*\w+)\b",
        r"\b(likely.*mental.*health|mental.*health.*risk)\b",
        r"\b(psycho.*analysis|psychological.*profile)\b",
        r"\b(personality.*type|personality.*trait)\b",
        r"\b(intent.*to.*leave|likely.*to.*resign)\b",
        r"\b(emotional.*state|emotional.*stability)\b"
    ]
    
    for pattern in individual_profiling_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 HR GOVERNANCE: Removed individual profiling pattern: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Individual Profiling]", report, flags=re.IGNORECASE)
    
    # Reject demographic/protected attribute inferences
    discrimination_patterns = [
        r"\b(age.*pattern|older.*workers|younger.*workers|millennial|gen.*x|gen.*z)\b",
        r"\b(gender.*difference|by.*gender|men.*vs.*women|more.*female|more.*male)\b",
        r"\b(race.*pattern|ethnic.*difference|by.*race|racial.*group)\b",
        r"\b(protected.*class.*inference|discrimination|bias)\b",
        r"\b(immigrant.*pattern|citizenship.*status|national.*origin)\b",
        r"\b(religious.*pattern|disability.*pattern)\b",
        r"\b(sexual.*orientation|gender.*identity)\b",
        r"\b(marital.*status.*pattern|family.*status)\b",
        r"\b(mothers|fathers|parents|childcare)\b"  # Avoid inference about parental status
    ]
    
    for pattern in discrimination_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 HR GOVERNANCE: Removed demographic inference: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Protected Attribute]", report, flags=re.IGNORECASE)
    
    # Reject individual performance comparisons (no ranking)
    individual_comparison_patterns = [
        r"\b(top.*performer|best.*employee|worst.*employee|poorest.*performer)\b",
        r"\b(highest.*ranked|lowest.*ranked)\b",
        r"\b(underperform|outperform|perform(ing|ance).*metric)\b",
        r"\b(star.*employee|problem.*employee)\b"
    ]
    
    for pattern in individual_comparison_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 HR GOVERNANCE: Removed individual ranking: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Individual Ranking]", report, flags=re.IGNORECASE)
    
    return report


def validate_banking_claims(report):
    """
    BANKING-SPECIFIC GOVERNANCE FILTER
    Removes speculation about customer solvency/creditworthiness at individual level.
    Ensures compliance with Fair Lending, FCRA, ECOA.
    """
    # Reject individual credit worthiness assumptions
    credit_patterns = [
        r"\b(customer.*is.*risky|customer.*is.*high.*risk)\b",
        r"\b(unlikely.*to.*pay|likely.*to.*default)\b",
        r"\b(creditworthiness.*assessment|credit.*profile.*analysis)\b"
    ]
    
    for pattern in credit_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 BANKING GOVERNANCE: Removed credit assessment: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Individual Credit Assessment]", report, flags=re.IGNORECASE)
    
    return report


def validate_pharma_claims(report):
    """
    PHARMA-SPECIFIC GOVERNANCE FILTER
    Removes safety claims that could trigger FDA liability.
    Ensures clinical rigor in adverse event language.
    """
    # Reject unverified clinical claims
    clinical_patterns = [
        r"\b(safe|unsafe|dangerous|toxic)\b(?!.*\[source)",  # Must have source attribution
        r"\b(likely.*cause.*harm|certain.*to.*cause)\b",
        r"\b(proven.*effective|proven.*ineffective)\b",  # Only use in approved indications
        r"\b(should.*be.*recalled|product.*recall.*recommended)\b"  # Only FDA can mandate recalls
    ]
    
    for pattern in clinical_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 PHARMA GOVERNANCE: Removed unverified clinical claim: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Clinical Claim]", report, flags=re.IGNORECASE)
    
    return report


def validate_retail_claims(report):
    """
    RETAIL-SPECIFIC GOVERNANCE FILTER
    Removes discriminatory store performance assumptions.
    Ensures no race/ethnicity-based location analysis.
    """
    # Reject location-based demographic profiling
    location_patterns = [
        r"\b(urban.*store|rural.*store|store.*in.*neighborhood).*(?:perform|fail|struggle)\b",
        r"\b(underserved.*market|low.*income.*area)\b",
        r"\b(demographic.*target|demographic.*analysis)\b"
    ]
    
    for pattern in location_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 RETAIL GOVERNANCE: Removed location-based demographic analysis: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Location Analysis]", report, flags=re.IGNORECASE)
    
    return report


def validate_logistics_claims(report):
    """
    LOGISTICS-SPECIFIC GOVERNANCE FILTER
    Removes over-personalization of driver/carrier performance.
    """
    # Reject individual carrier/driver blame without systemic context
    driver_patterns = [
        r"\b(driver.*incompetence|driver.*at.*fault)\b",
        r"\b(carrier.*is.*failing|carrier.*is.*unreliable)\b",
        r"\b(driver.*error.*caused)\b"
    ]
    
    for pattern in driver_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 LOGISTICS GOVERNANCE: Removed individual blame: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Individual Accountability]", report, flags=re.IGNORECASE)
    
    return report


def validate_ecommerce_claims(report):
    """
    E-COMMERCE-SPECIFIC GOVERNANCE FILTER
    Removes personalized user behavior profiling without consent language.
    """
    # Reject individual customer profiling
    user_patterns = [
        r"\b(customer.*behavior.*indicates|customer.*is.*likely.*to)\b",
        r"\b(prediction.*about.*user|user.*will.*purchase)\b"
    ]
    
    for pattern in user_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 ECOMMERCE GOVERNANCE: Removed customer profiling: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - User Profiling]", report, flags=re.IGNORECASE)
    
    return report


def validate_manufacturing_claims(report):
    """
    MANUFACTURING-SPECIFIC GOVERNANCE FILTER
    Removes individual worker blame without systemic analysis.
    """
    # Reject individual worker blame
    worker_patterns = [
        r"\b(worker.*error.*caused|operator.*failure)\b",
        r"\b(employee.*at.*fault|staff.*incompetence)\b"
    ]
    
    for pattern in worker_patterns:
        if re.search(pattern, report, flags=re.IGNORECASE):
            print(f"🚫 MANUFACTURING GOVERNANCE: Removed worker blame: {pattern}")
            report = re.sub(pattern, "[GOVERNANCE FILTERED - Process Analysis]", report, flags=re.IGNORECASE)
    
    return report


# ==========================================
# LAYER 3: MASTER GOVERNANCE ROUTER
# ==========================================

def apply_industry_governance(report, industry):
    """
    Routes report through appropriate industry-specific governance filters.
    All reports go through universal filters first, then industry-specific.
    """
    # Universal governance always applies
    report = validate_operational_claims(report)
    report = downgrade_theatrics(report)
    
    # Industry-specific governance
    if industry.lower() == "hr":
        report = validate_hr_claims(report)
    elif industry.lower() == "banking":
        report = validate_banking_claims(report)
    elif industry.lower() == "pharma":
        report = validate_pharma_claims(report)
    elif industry.lower() == "retail":
        report = validate_retail_claims(report)
    elif industry.lower() == "logistics":
        report = validate_logistics_claims(report)
    elif industry.lower() == "ecommerce":
        report = validate_ecommerce_claims(report)
    elif industry.lower() == "manufacturing":
        report = validate_manufacturing_claims(report)
    
    return report


# ==========================================
# LAYER 4: CONTENT AUDIT TRAIL
# ==========================================

def audit_governance_changes(original_report, filtered_report):
    """
    Logs all governance changes for audit purposes.
    Helps track what was filtered and why.
    """
    original_length = len(original_report)
    filtered_length = len(filtered_report)
    chars_removed = original_length - filtered_length
    
    if chars_removed > 0:
        print(f"📋 GOVERNANCE AUDIT: Removed {chars_removed} characters")
        print(f"   Original length: {original_length}, Filtered length: {filtered_length}")
    
    return {
        "original_length": original_length,
        "filtered_length": filtered_length,
        "chars_removed": chars_removed,
        "audit_timestamp": __import__('datetime').datetime.now().isoformat()
    }
