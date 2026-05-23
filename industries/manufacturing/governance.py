def validate_operational_claims(report):
    """
    Scans the AI text and downgrades absolute claims 
    to professional, probabilistic consulting language.
    """
    prohibited_terms = {
        "caused by": "may be associated with",
        "definitely": "likely",
        "guarantees": "suggests a high probability of",
        "certainly due to": "potentially driven by",
        "proves that": "indicates that",
        "will result in": "could result in"
    }
    
    for bad_word, safe_word in prohibited_terms.items():
        # Using regex to match whole words/phrases ignoring case
        import re
        report = re.sub(rf'\b{bad_word}\b', safe_word, report, flags=re.IGNORECASE)
        
    return report

def inject_reliability_warning(report, avg_confidence):
    """If the overall data is weak, permanently brand the report as cautious."""
    if avg_confidence < 0.65:
        warning = "\n> **⚠️ GOVERNANCE WARNING:** Several operational findings in this report rely on fragmented or low-confidence data. Interpret these specific signals cautiously until further telemetry is validated.\n\n"
        # Inject right under the Executive Summary header
        report = report.replace("# 1. Executive Situation Report", f"# 1. Executive Situation Report{warning}")
        
    return report
