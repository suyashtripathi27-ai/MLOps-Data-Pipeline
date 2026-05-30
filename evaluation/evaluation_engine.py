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
        synonyms = self.metadata.get("concept_synonyms", {}).get(concept_key, [])
        if not synonyms: return 0.0
        hits = sum(1 for synonym in synonyms if synonym.lower() in search_text)
        if hits == 0: return 0.0
        elif hits == 1: return 0.6
        else: return 1.0

    def _evaluate_behavior(self):
        score = 0.0
        primary = self.metadata.get("expected_primary_risk")
        secondary = self.metadata.get("expected_secondary_risks", [])
        max_points = 10 / (1 + len(secondary))
        if primary:
            score += self._check_concept_presence(primary, self.report_lower) * max_points
        for sec_risk in secondary:
            score += self._check_concept_presence(sec_risk, self.report_lower) * max_points
        self.scorecard.scores["behavioral_intelligence"] = round(score)

    def _evaluate_prioritization(self):
        primary = self.metadata.get("expected_primary_risk")
        if not primary:
            self.scorecard.scores["prioritization"] = 10
            return
        priority_match = re.search(r'(# 1\..*?# 2\.|# 3\..*?# 4\.)', self.report, re.DOTALL | re.IGNORECASE)
        priority_text = priority_match.group(0).lower() if priority_match else ""
        confidence = self._check_concept_presence(primary, priority_text)
        self.scorecard.scores["prioritization"] = round(confidence * 10)

    def _evaluate_governance(self):
        score = 10
        gov_rules = self.metadata.get("governance_expectation", {})
        mentions_missing = any(word in self.report_lower for word in ["excluded", "missing", "visibility constraint", "unavailable"])
        
        if gov_rules.get("must_acknowledge_missing_data"):
            if not mentions_missing: score -= 5
        else:
            if mentions_missing: score -= 3
                
        if gov_rules.get("must_not_overstate_certainty"):
            if any(w in self.report_lower for w in ["proves", "guarantees", "certainly"]):
                score -= 5
        self.scorecard.scores["governance"] = max(0, score)

    def _evaluate_industry_realism(self):
        industry = self.metadata.get("industry")
        expected_terms = self.vocab_dict.get(industry, [])
        if not expected_terms:
            self.scorecard.scores["industry_realism"] = 10
            return
        terms_found = sum(1 for term in expected_terms if term.lower() in self.report_lower)
        self.scorecard.scores["industry_realism"] = min(10, round((terms_found / min(3, len(expected_terms))) * 10))

    def _evaluate_structure(self):
        score = 10
        for header in ["# 1.", "# 2.", "# 3.", "# 4.", "# 5."]:
            if header not in self.report: score -= 2
        self.scorecard.scores["executive_readability"] = max(0, score)

    def run_evaluation(self):
        self._evaluate_structure()
        self._evaluate_behavior()
        self._evaluate_prioritization()
        self._evaluate_governance()
        self._evaluate_industry_realism()
        return self.scorecard.get_report()
