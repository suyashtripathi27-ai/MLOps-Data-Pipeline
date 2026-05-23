# Ontology Architecture (Contextual + Governed)

This document defines the production ontology architecture introduced to resolve six critical risks:

1. **Ontology collision risk**: keyword collisions (e.g., `turnover`) are disambiguated with `context_type`, `required_context`, and `forbidden_cooccurrence`.
2. **Missing operational dimensions**: positive (`growth_stability_cluster`, `operational_resilience_cluster`, `customer_loyalty_cluster`) and neutral (`operational_efficiency_cluster`) clusters complement risk clusters.
3. **Static time dynamics**: trajectory metadata (`state_mode`, `trajectory_direction`, `trend_indicators`, `lookback_window`, `baseline_comparison`) separates state from trend.
4. **No industry governance layer**: banking, pharma, HR, and ecommerce governance profiles clamp unsafe claims and add compliance constraints.
5. **Missing e-commerce vertical**: ecommerce now includes `conversion_friction_cluster`, `retention_risk_cluster`, `fulfillment_instability_cluster`, and `promotion_dependency_cluster`.
6. **Shallow cluster depth**: hierarchy now supports `cluster -> subcluster -> signal_family -> specific_metric` for granular reasoning.

## Files

- `ontology/base_ontology.json`: contextual cluster taxonomy by industry.
- `ontology/governance_profiles.json`: per-industry claim safety and compliance constraints.
- `ontology/temporal_extensions.json`: trend/velocity/acceleration/volatility semantics.
- `ontology/polarity_clusters.json`: positive/neutral/risk balancing clusters.
- `utils/contextual_matcher.py`: matching, temporal tagging, governance clamping, and contextual schema routing.

## Matching flow

1. Build candidate catalog from base ontology + polarity clusters.
2. Score candidate clusters by keyword hits, required-context hits, and context-type alignment.
3. Reject candidates with forbidden co-occurrence.
4. Return best match with hierarchy metadata and temporal interpretation.
5. Clamp risky language using governance profile before final signal output.

## Governance examples

- **Banking AML**: disallow definitive fraud wording (`fraud_detected`), replace with `anomaly_flagged`, and clamp maximum severity.
- **Pharma compliance**: enforce GMP/FDA-aligned compliance-safe wording.
- **HR**: apply demographic safety checks and avoid protected-attribute inferences.

## Temporal semantics

Each signal receives:

- `state_mode`: `state` or `trajectory`
- `trajectory_direction`: `improving`, `declining`, or `stable`
- `trend_indicators`: `velocity`, `acceleration`, `volatility`
- `lookback_window` and `baseline_comparison`

This makes `declining margin` materially different from `stable low margin` in downstream reasoning.
