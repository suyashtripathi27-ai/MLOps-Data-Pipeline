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
        if not synonyms:
            return 0.0
            
        hits = sum(1 for synonym in synonyms if synonym.lower() in search_text)
        
        # 📈 V2: Smoother Behavioral Scaling (Rewards concise writing)
        if hits == 0:
            return 0.0
        elif hits == 1:
            return 0.6
        elif hits == 2:
            return 0.85
        else:
            return 1.0

    def _evaluate_behavior(self):
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
        primary = self.metadata.get("expected_primary_risk")
        if not primary:
            self.scorecard.scores["prioritization"] = 10
            return

        priority_match = re.search(r'(# 1\..*?# 2\.|# 3\..*?# 4\.)', self.report, re.DOTALL | re.IGNORECASE)
        priority_text = priority_match.group(0).lower() if priority_match else ""

        synonyms = self.metadata.get("concept_synonyms", {}).get(primary, [])
        hits = sum(1 for synonym in synonyms if synonym.lower() in priority_text)
        
        if hits >= 1:
            self.scorecard.scores["prioritization"] = 10
        else:
            self.scorecard.scores["prioritization"] = 0

    def _evaluate_traceability(self):
        """📈 V2: Checks if recommendations logically trace back to identified risks."""
        expected_recs = self.metadata.get("expected_recommendations", [])
        if not expected_recs:
            self.scorecard.scores["recommendation_traceability"] = 10
            return

        match = re.search(r'# 4\..*?(?=# 5\.)', self.report, re.DOTALL | re.IGNORECASE)
        directives_text = match.group(0).lower() if match else ""
        
        if not directives_text:
            self.scorecard.scores["recommendation_traceability"] = 0
            return

        score = 0
        points_per_rec = 10 / len(expected_recs)
        
        for rec in expected_recs:
            synonyms = self.metadata.get("concept_synonyms", {}).get(rec, [])
            hits = sum(1 for synonym in synonyms if synonym.lower() in directives_text)
            if hits >= 1:
                score += points_per_rec
                
        self.scorecard.scores["recommendation_traceability"] = round(score)

    def _evaluate_governance(self):
        """📈 V2: Strict Domain-Level Governance Checking"""
        score = 0.0
        gov_rules = self.metadata.get("governance_expectation", {})
        expected_domains = self.metadata.get("expected_governance_domains", [])

        if not gov_rules.get("must_acknowledge_missing_data"):
            self.scorecard.scores["governance"] = 10
            return

        # Dimension 1: General Acknowledgement (2.5 pts)
        if any(w in self.report_lower for w in ["excluded", "missing", "visibility constraint", "unavailable"]):
            score += 2.5

        # Dimension 2: Strict Domain Transparency (2.5 pts)
        if expected_domains:
            domain_hits = sum(1 for d in expected_domains if d.lower() in self.report_lower)
            if domain_hits == len(expected_domains):
                score += 2.5  # Full points: Named every missing domain
            elif domain_hits >= 1:
                score += 1.0  # Partial points: Named at least one
        else:
            score += 2.5

        # Dimension 3: Impact Disclosure (2.5 pts)
        impact_phrases = ["limits assessment", "interpret primarily", "rather than", "affect conclusions", "portfolio observations"]
        if any(p in self.report_lower for p in impact_phrases):
            score += 2.5

        # Dimension 4: Overstatement Detection (2.5 pts)
        overstatements = ["proves", "guarantees", "certainly", "100%", "definitely"]
        if not any(w in self.report_lower for w in overstatements):
            score += 2.5

        # Hallucination Penalty
        claims_no_exclusions = any(phrase in self.report_lower for phrase in [
            "no specific metrics were explicitly identified",
            "no specific metrics were excluded",
            "all data was available"
        ])
        
        if claims_no_exclusions:
            score -= 5.0
            
        self.scorecard.scores["governance"] = max(0, round(score))

    def _evaluate_industry_realism(self):
        industry = self.metadata.get("industry")
        vocab_data = self.vocab_dict.get(industry, {})
        
        if isinstance(vocab_data, list):
            tier1, tier2 = vocab_data, []
        else:
            tier1 = vocab_data.get("tier1", [])
            tier2 = vocab_data.get("tier2", [])
            
        score = 0.0
        t1_hits = 0
        t2_hits = 0
        
        if tier1:
            t1_hits = sum(1 for term in tier1 if term.lower() in self.report_lower)
            score += min(7.0, (t1_hits / min(3, len(tier1))) * 7.0)
            
        if tier2:
            t2_hits = sum(1 for term in tier2 if term.lower() in self.report_lower)
            score += min(3.0, (t2_hits / min(2, len(tier2))) * 3.0)
            
        # 🔍 ADDED: Deep telemetry to diagnose Realism scores
        print("\n🔍 DEBUG REALISM:")
        print(f"  -> Industry: {industry}")
        print(f"  -> Tier 1 Hits: {t1_hits} / {len(tier1)}")
        print(f"  -> Tier 2 Hits: {t2_hits} / {len(tier2)}")
        print(f"  -> FINAL REALISM SCORE: {round(score)}\n")
            
        self.scorecard.scores["industry_realism"] = round(score)

    def _evaluate_structure(self):
        required_headers = ["# 1.", "# 2.", "# 3.", "# 4.", "# 5."]
        score = 10
        for header in required_headers:
            if header not in self.report:
                score -= 2
        self.scorecard.scores["executive_readability"] = max(0, score)

    def run_evaluation(self):
        self._evaluate_structure()
        self._evaluate_behavior()
        self._evaluate_prioritization()
        self._evaluate_traceability()
        self._evaluate_governance()
        self._evaluate_industry_realism()
        return self.scorecard.get_report()
