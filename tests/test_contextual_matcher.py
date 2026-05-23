import unittest

from utils.contextual_matcher import (
    apply_governance,
    detect_industry_from_columns,
    detect_temporal_dynamics,
    match_ontology_signal,
)


class ContextualMatcherTests(unittest.TestCase):
    def test_turnover_disambiguation_across_contexts(self):
        hr_match = match_ontology_signal(
            category="Workforce",
            name="Employee turnover ratio",
            warning="HIGH",
            industry="manufacturing",
        )
        inventory_match = match_ontology_signal(
            category="Inventory",
            name="Inventory turnover ratio",
            warning="HIGH",
            industry="retail",
        )
        finance_match = match_ontology_signal(
            category="Financial Performance",
            name="Asset turnover ratio",
            warning="HIGH",
            industry="finance",
        )

        self.assertEqual(hr_match["cluster"], "workforce_risk_cluster")
        self.assertEqual(inventory_match["cluster"], "inventory_health_cluster")
        self.assertEqual(finance_match["cluster"], "margin_erosion_cluster")

    def test_governance_clamps_banking_fraud_claims(self):
        finding, severity, governance = apply_governance(
            industry="banking",
            cluster_name="aml_fraud_cluster",
            finding="Transaction stream indicates fraud_detected across accounts",
            severity="HIGH",
        )

        self.assertIn("anomaly_flagged", finding)
        self.assertEqual(severity, "MEDIUM")
        self.assertTrue(governance["severity_clamped"])

    def test_temporal_dynamics_detects_declining_vs_stable(self):
        declining = detect_temporal_dynamics("declining margin with accelerating volatile swings")
        stable = detect_temporal_dynamics("stable low margin and consistent run-rate")

        self.assertEqual(declining["trajectory_direction"], "declining")
        self.assertEqual(stable["trajectory_direction"], "stable")
        self.assertEqual(declining["trend_indicators"]["acceleration"], "increasing")
        self.assertEqual(stable["trend_indicators"]["volatility"], "low")

    def test_contextual_industry_routing_supports_ecommerce(self):
        industry, metadata = detect_industry_from_columns(
            ["session_id", "cart_abandonment", "checkout_conversion", "repeat_purchase_rate", "order_id"]
        )

        self.assertEqual(industry, "ecommerce")
        self.assertTrue(metadata["keyword_hits"])


if __name__ == "__main__":
    unittest.main()
