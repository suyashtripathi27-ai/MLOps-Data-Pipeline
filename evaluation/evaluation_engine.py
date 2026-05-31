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

    def _extract_section(self, start_header: str, end_header: str) -> str:
        """Helper to extract text between two Markdown headers."""
        pattern = re.compile(rf'({start_header}.*?)(?={end_header}|\Z)', re.DOTALL | re.IGNORECASE)
        match = pattern.search(self.report)
        return match.group(0).lower() if match else ""

    def _check_concept_presence(self, concept_key: str, search_text: str) -> float:
        synonyms = self.metadata.get("concept_synonyms", {}).get(concept_key, [])
        if not synonyms:
            return 0.0
            
        hits = sum(1 for synonym in synonyms if synonym.lower() in search_text)
        
        if hits == 0: return 0.0
        elif hits == 1: return 0.6
        elif hits == 2: return 0.85
        else: return 1.0

    def _evaluate_behavior(self):
        score = 0.0
        primary = self.metadata.get("expected_primary_risk")
        secondary = self.metadata.get("expected_secondary_risks", [])
        
        total_concepts = 1 + len(secondary)
        max_points_per_concept = 10 / total_concepts

        if primary:
            score += self._check_concept_presence(primary, self.report_lower) * max_points_per_concept
            
        for sec_risk in secondary:
            score += self._check_concept_presence(sec_risk, self.report_lower) * max_points_per_concept
                
        self.scorecard.scores["behavioral_intelligence"] = round(score)

    def _evaluate_prioritization(self):
        """📈 V3: Tiered location-based scoring."""
        primary = self.metadata.get("expected_primary_risk")
        if not primary:
            self.scorecard.scores["prioritization"] = 10
            return

        synonyms = self.metadata.get("concept_synonyms", {}).get(primary, [])
        
        exec_summary = self._extract_section(r'# 1\.', r'# 2\.')
        priority_section = self._extract_section(r'# 3\.', r'# 4\.')
        
        in_priority = any(syn.lower() in priority_section for syn in synonyms)
        in_exec = any(syn.lower() in exec_summary for syn in synonyms)
        in_report = any(syn.lower() in self.report_lower for syn in synonyms)

        if in_priority:
            self.scorecard.scores["prioritization"] = 10  # Placed exactly where it belongs
        elif in_exec:
            self.scorecard.scores["prioritization"] = 6   # Mentioned in intro, but not analyzed deeply
        elif in_report:
            self.scorecard.scores["prioritization"] = 3   # Buried somewhere in the text
        else:
            self.scorecard.scores["prioritization"] = 0

    def _evaluate_traceability(self):
        """📈 V3: Checks primary concepts AND dedicated recommendation synonyms."""
        expected_recs = self.metadata.get("expected_recommendations", [])
        if not expected_recs:
            self.scorecard.scores["recommendation_traceability"] = 10
            return

        directives_text = self._extract_section(r'# 4\.', r'# 5\.')
        if not directives_text:
            self.scorecard.scores["recommendation_traceability"] = 0
            return

        score = 0
        points_per_rec = 10 / len(expected_recs)
        
        for rec in expected_recs:
            synonyms = self.metadata.get("concept_synonyms", {}).get(rec, [])
            rec_syns = self.metadata.get("recommendation_synonyms", {}).get(rec, [])
            all_syns = synonyms + rec_syns  # Combine both lists!
            
            hits = sum(1 for syn in all_syns if syn.lower() in directives_text)
            if hits >= 1:
                score += points_per_rec
                
        self.scorecard.scores["recommendation_traceability"] = round(score)

    def _evaluate_governance(self):
        score = 0.0
        gov_rules = self.metadata.get("governance_expectation", {})
        expected_domains = self.metadata.get("expected_governance_domains", [])

        if not gov_rules.get("must_acknowledge_missing_data"):
            self.scorecard.scores["governance"] = 10
            return

        if any(w in self.report_lower for w in ["excluded", "missing", "visibility constraint", "unavailable"]):
            score += 2.5

        if expected_domains:
            domain_hits = sum(1 for d in expected_domains if d.lower() in self.report_lower)
            if domain_hits == len(expected_domains): score += 2.5
            elif domain_hits >= 1: score += 1.0
        else:
            score += 2.5

        impact_phrases = ["limits assessment", "interpret primarily", "rather than", "affect conclusions", "portfolio observations"]
        if any(p in self.report_lower for p in impact_phrases):
            score += 2.5

        overstatements = ["proves", "guarantees", "certainly", "100%", "definitely"]
        if not any(w in self.report_lower for w in overstatements):
            score += 2.5

        claims_no_exclusions = any(phrase in self.report_lower for phrase in [
            "no specific metrics were explicitly identified", "no specific metrics were excluded", "all data was available"
        ])
        
        if claims_no_exclusions:
            score -= 5.0
            
        self.scorecard.scores["governance"] = max(0, round(score))

    def _evaluate_industry_realism(self):
        """📈 V3: Surgical Missing-Term Debugger"""
        industry = self.metadata.get("industry")
        vocab_data = self.vocab_dict.get(industry, {})
        
        tier1 = vocab_data.get("tier1", []) if isinstance(vocab_data, dict) else vocab_data
        tier2 = vocab_data.get("tier2", []) if isinstance(vocab_data, dict) else []
            
        t1_found = [term for term in tier1 if term.lower() in self.report_lower]
        t1_missing = [term for term in tier1 if term.lower() not in self.report_lower]
        
        t2_found = [term for term in tier2 if term.lower() in self.report_lower]
        t2_missing = [term for term in tier2 if term.lower() not in self.report_lower]
        
        score = 0.0
        if tier1: score += min(7.0, (len(t1_found) / min(3, len(tier1))) * 7.0)
        if tier2: score += min(3.0, (len(t2_found) / min(2, len(tier2))) * 3.0)
            
        print(f"\n🔍 DEBUG REALISM [{industry.upper()}]:")
        print(f"  -> Tier 1 Hits ({len(t1_found)}): {', '.join(t1_found) if t1_found else 'None'}")
        print(f"  -> Tier 1 Missing: {', '.join(t1_missing)}")
        print(f"  -> Tier 2 Hits ({len(t2_found)}): {', '.join(t2_found) if t2_found else 'None'}")
        print(f"  -> Tier 2 Missing: {', '.join(t2_missing)}")
        print(f"  -> FINAL REALISM SCORE: {round(score)}\n")
            
        self.scorecard.scores["industry_realism"] = round(score)

    def _evaluate_structure(self):
        required_headers = ["# 1.", "# 2.", "# 3.", "# 4.", "# 5."]
        score = 10
        for header in required_headers:
            if header not in self.report: score -= 2
        self.scorecard.scores["executive_readability"] = max(0, score)

    def run_evaluation(self):
        self._evaluate_structure()
        self._evaluate_behavior()
        self._evaluate_prioritization()
        self._evaluate_traceability()
        self._evaluate_governance()
        self._evaluate_industry_realism()
        return self.scorecard.get_report()
