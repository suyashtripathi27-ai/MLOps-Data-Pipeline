import re

def validate_operational_claims(report):
    """
    Scans the AI text and downgrades absolute claims to probabilistic consulting language.
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
    """
    Hunts down AI-generated alarmist adjectives and replaces them with 
    calm, proportional executive language.
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
        r"\b(pervasive)\b": "distributed"
    }
    
    for pattern, safe_word in theatrics.items():
        report = re.sub(pattern, safe_word, report, flags=re.IGNORECASE)
        
    return report

def inject_reliability_warning(report, avg_confidence):
    """If the overall data is weak, permanently brand the report as cautious."""
    if avg_confidence < 0.65:
        warning = "\n> **⚠️ GOVERNANCE WARNING:** Several operational findings in this report rely on fragmented or low-confidence data. Interpret these specific signals cautiously until further telemetry is validated.\n\n"
        report = report.replace("# 1. Executive Situation Report", f"# 1. Executive Situation Report{warning}")
        
    return report
