import json
import re
from evaluation.scorecard import Scorecard

class EvaluationEngine:
    def __init__(self, report_markdown: str, metadata_path: str, vocab_path: str):
        self.report = report_markdown
        self.report_lower = report_markdown.lower()
        
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
            
        with open(vocab_path, 'r') as f:
            self.vocab_dict = json.load(f)
            
        self.scorecard = Scorecard()

    def _check_concept_presence(self, concept_key: str, search_text: str) -> float:
        """Returns a confidence score (0.0 to 1.0) based on synonym hits."""
        synonyms = self.metadata.get("concept_synonyms", {}).get(concept_key, [])
        if not synonyms:
            return 0.0
            
        # Count unique synonym hits
        hits = sum(1 for synonym in synonyms if synonym.lower() in search_text)
        
        if hits == 0:
            return 0.0
        elif hits == 1:
            return 0.6
        else:
            return 1.0

    def _evaluate_behavior(self):
        """Validates if expected primary and secondary risks were discussed."""
        score = 0.0
        primary = self.metadata.get("expected_primary_risk")
        secondary = self.metadata.get("expected_secondary_risks", [])
        
        total_concepts = 1 + len(secondary)
        max_points_per_concept = 10 / total_concepts

        if primary:
            confidence = self._check_concept_presence(primary, self.report_lower)
            score += confidence * max_points_per_concept
            
        for sec_risk in secondary:
            confidence = self._check_concept_presence(sec_risk, self.report_lower)
            score += confidence * max_points_per_concept
                
        self.scorecard.scores["behavioral_intelligence"] = round(score)

    def _evaluate_prioritization(self):
        """Checks if the PRIMARY risk was elevated to the priority/stoplight sections."""
        primary = self.metadata.get("expected_primary_risk")
        if not primary:
            self.scorecard.scores["prioritization"] = 10
            return

        # Extract just the top priority section (Section 1 or 3)
        priority_match = re.search(r'(# 1\..*?# 2\.|# 3\..*?# 4\.)', self.report, re.DOTALL | re.IGNORECASE)
        priority_text = priority_match.group(0).lower() if priority_match else ""

        # Fetch synonyms directly to check for ANY hit
        synonyms = self.metadata.get("concept_synonyms", {}).get(primary, [])
        hits = sum(1 for synonym in synonyms if synonym.lower() in priority_text)
        
        # 🛑 THE FIX: If it hit the concept AT ALL in the priority section, full points!
        if hits >= 1:
            self.scorecard.scores["prioritization"] = 10
        else:
            self.scorecard.scores["prioritization"] = 0

    def _evaluate_governance(self):
        """Evaluates governance contextually based on expectations, checking for hallucinations."""
        score = 10
        gov_rules = self.metadata.get("governance_expectation", {})
        
        # Check missing data acknowledgment
        mentions_missing = any(word in self.report_lower for word in ["excluded", "missing", "visibility constraint", "unavailable"])
        
        # 🛑 Governance Consistency Check (Catches logical contradictions)
        claims_no_exclusions = any(phrase in self.report_lower for phrase in [
            "no specific metrics were explicitly identified",
            "no specific metrics were excluded",
            "no metrics were excluded",
            "all available statistical summary data points were leveraged",
            "all data was available",
            "no system warnings reported"
        ])
        
        if gov_rules.get("must_acknowledge_missing_data"):
            if not mentions_missing:
                score -= 5 # Failed to mention known data gaps
            
            # If it was SUPPOSED to acknowledge missing data, but explicitly claimed none was missing
            if claims_no_exclusions:
                score -= 7 # Critical hallucination deduction
        else:
            if mentions_missing:
                score -= 3 # Hallucinated a data gap that didn't exist
                
        # Check certainty overstatement
        if gov_rules.get("must_not_overstate_certainty"):
            overstatements = ["proves", "guarantees", "certainly", "100%"]
            if any(word in self.report_lower for word in overstatements):
                score -= 5

        self.scorecard.scores["governance"] = max(0, score)

    def _evaluate_industry_realism(self):
        """Checks if the report uses the correct enterprise vocabulary."""
        industry = self.metadata.get("industry")
        expected_terms = self.vocab_dict.get(industry, [])
        
        print(f"\n🔍 DEBUG REALISM - Industry Key from Metadata: '{industry}'")
        print(f"🔍 DEBUG REALISM - Available Dictionary Keys: {list(self.vocab_dict.keys())}")
        print(f"🔍 DEBUG REALISM - Expected Terms Loaded: {expected_terms}\n")
        
        if not expected_terms:
            self.scorecard.scores["industry_realism"] = 0
            return
            
        terms_found = sum(1 for term in expected_terms if term.lower() in self.report_lower)
        
        # Give full points if they use at least 3 strong industry terms
        ratio = terms_found / min(3, len(expected_terms))
        self.scorecard.scores["industry_realism"] = min(10, round(ratio * 10))

    def _evaluate_structure(self):
        """Basic check for required Markdown headers."""
        required_headers = ["# 1.", "# 2.", "# 3.", "# 4.", "# 5."]
        score = 10
        for header in required_headers:
            if header not in self.report:
                score -= 2
        self.scorecard.scores["executive_readability"] = max(0, score)

    def run_evaluation(self):
        """Executes all checks and returns the scorecard."""
        self._evaluate_structure()
        self._evaluate_behavior()
        self._evaluate_prioritization()
        self._evaluate_governance()
        self._evaluate_industry_realism()
        
        return self.scorecard.get_report()
