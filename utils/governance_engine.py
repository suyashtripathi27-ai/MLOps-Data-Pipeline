import re

def validate_operational_claims(report):
    """
    UNIVERSAL CLAIM VALIDATOR: Downgrades absolute claims to probabilistic consulting language.
    Applies to Manufacturing, HR, E-commerce, etc.
    """
    prohibited_terms = {
        "caused by": "may be associated with",
        "definitely": "likely",
        "guarantees": "suggests a high probability of",
        "certainly due to": "potentially driven by",
        "proves that": "indicates that",
        "will result in": "could result in",
        "is already creating": "may be contributing to",
        "direct consequence": "potential consequence"
    }
    
    for bad_word, safe_word in prohibited_terms.items():
        report = re.sub(rf'\b{bad_word}\b', safe_word, report, flags=re.IGNORECASE)
        
    return downgrade_theatrics(report)

def downgrade_theatrics(report):
    """UNIVERSAL THEATRICS DOWNGRADER: Strips alarmist adjectives."""
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
        r"\b(pervasive)\b": "distributed"
    }
    
    for pattern, safe_word in theatrics.items():
        report = re.sub(pattern, safe_word, report, flags=re.IGNORECASE)
        
    return report

def inject_reliability_warning(report, avg_confidence):
    """UNIVERSAL LIABILITY SHIELD"""
    if avg_confidence < 0.65:
        warning = "\n> **⚠️ GOVERNANCE WARNING:** Several findings in this report rely on fragmented or low-confidence data. Interpret these specific signals cautiously until further telemetry is validated.\n\n"
        report = report.replace("# 1. Executive Situation Report", f"# 1. Executive Situation Report{warning}")
        
    return report
