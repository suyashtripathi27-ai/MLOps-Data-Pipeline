import os
import json
import csv
from datetime import datetime
from evaluation.evaluation_engine import EvaluationEngine

def get_scenario_from_filename(filename: str, industry: str) -> str:
    """Universally routes the dataset to the correct scenario across all 64 architectures."""
    lower_name = filename.lower()
    
    if industry == "hr":
        if any(w in lower_name for w in ["attrition", "turnover", "retention"]): return "attrition_crisis"
        if any(w in lower_name for w in ["burnout", "wellbeing", "overtime"]): return "burnout_risk"
        if any(w in lower_name for w in ["recruit", "hire", "talent"]): return "recruitment_failure"
        if any(w in lower_name for w in ["learning", "training", "skill"]): return "learning_impact_failure"
        if any(w in lower_name for w in ["leader", "succession"]): return "leadership_gap"
        if any(w in lower_name for w in ["workforce", "headcount", "capacity"]): return "workforce_planning_risk"
        if any(w in lower_name for w in ["diversity", "inclusion", "equity"]): return "diversity_inclusion_risk"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "attrition_crisis"
        
    elif industry == "retail":
        if any(w in lower_name for w in ["store", "footfall", "performance"]): return "store_performance_decline"
        if any(w in lower_name for w in ["inventory", "stock", "aging"]): return "inventory_health_failure"
        if any(w in lower_name for w in ["markdown", "clearance"]): return "markdown_pressure"
        if any(w in lower_name for w in ["shrinkage", "theft", "loss"]): return "shrinkage_risk"
        if any(w in lower_name for w in ["price", "pricing", "margin"]): return "pricing_pressure"
        if any(w in lower_name for w in ["promotion", "campaign"]): return "promotion_inefficiency"
        if any(w in lower_name for w in ["productivity", "labor", "staff"]): return "workforce_productivity_decline"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "store_performance_decline"

    elif industry == "finance":
        if any(w in lower_name for w in ["liquidity", "cash"]): return "liquidity_crisis"
        if any(w in lower_name for w in ["margin", "ebitda"]): return "margin_erosion"
        if any(w in lower_name for w in ["concentration", "revenue"]): return "revenue_concentration"
        if any(w in lower_name for w in ["forecast", "variance"]): return "forecast_breakdown"
        if any(w in lower_name for w in ["working capital", "receivable"]): return "working_capital_stress"
        if any(w in lower_name for w in ["covenant", "debt"]): return "debt_covenant_risk"
        if any(w in lower_name for w in ["inflation", "opex", "cost"]): return "cost_inflation_pressure"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "margin_erosion"

    elif industry == "ecommerce":
        if any(w in lower_name for w in ["churn", "retention", "clv"]): return "customer_churn"
        if any(w in lower_name for w in ["cart", "abandonment"]): return "cart_abandonment"
        if any(w in lower_name for w in ["cac", "acquisition", "roas"]): return "cac_explosion"
        if any(w in lower_name for w in ["inventory", "distortion"]): return "inventory_distortion"
        if any(w in lower_name for w in ["fulfillment", "delivery"]): return "fulfillment_breakdown"
        if any(w in lower_name for w in ["promotion", "discount"]): return "promotion_dependency"
        if any(w in lower_name for w in ["marketplace", "channel"]): return "marketplace_risk"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "customer_churn"

    elif industry == "manufacturing":
        if any(w in lower_name for w in ["oee", "instability", "production"]): return "production_instability"
        if any(w in lower_name for w in ["quality", "defect", "rework"]): return "quality_failure"
        if any(w in lower_name for w in ["maintenance", "mtbf"]): return "maintenance_failure"
        if any(w in lower_name for w in ["material", "shortage"]): return "material_shortage"
        if any(w in lower_name for w in ["capacity", "constraint"]): return "capacity_constraint"
        if any(w in lower_name for w in ["scrap", "waste"]): return "scrap_cost_explosion"
        if any(w in lower_name for w in ["supplier", "procurement"]): return "supplier_dependency"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "production_instability"

    elif industry == "pharma":
        if any(w in lower_name for w in ["compliance", "gmp", "fda"]): return "compliance_breach"
        if any(w in lower_name for w in ["yield", "batch"]): return "yield_degradation"
        if any(w in lower_name for w in ["cold chain", "temperature"]): return "cold_chain_failure"
        if any(w in lower_name for w in ["recall", "safety"]): return "market_recall_risk"
        if any(w in lower_name for w in ["sterility", "contamination"]): return "sterility_failure"
        if any(w in lower_name for w in ["deviation", "capa"]): return "deviation_spike"
        if any(w in lower_name for w in ["supplier", "quality"]): return "supplier_quality_risk"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "compliance_breach"

    elif industry == "logistics":
        if any(w in lower_name for w in ["bottleneck", "network", "throughput"]): return "network_bottleneck"
        if any(w in lower_name for w in ["freight", "cost", "fuel"]): return "freight_cost_pressure"
        if any(w in lower_name for w in ["warehouse", "congestion"]): return "warehouse_congestion"
        if any(w in lower_name for w in ["carrier", "concentration"]): return "carrier_concentration"
        if any(w in lower_name for w in ["sla", "breach", "service"]): return "sla_breach_crisis"
        if any(w in lower_name for w in ["route", "efficiency"]): return "route_efficiency_decline"
        if any(w in lower_name for w in ["asset", "utilization", "fleet"]): return "asset_utilization_failure"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "network_bottleneck"

    elif industry == "banking":
        if any(w in lower_name for w in ["churn", "attrition"]): return "churn_crisis"
        if any(w in lower_name for w in ["credit", "default", "loan"]): return "credit_deterioration"
        if any(w in lower_name for w in ["liquidity", "deposit"]): return "liquidity_pressure"
        if any(w in lower_name for w in ["aml", "fraud"]): return "aml_fraud_risk"
        if any(w in lower_name for w in ["relationship", "depth"]): return "relationship_depth_decline"
        if any(w in lower_name for w in ["concentration", "exposure"]): return "concentration_risk"
        if any(w in lower_name for w in ["governance", "missing", "data"]): return "governance_failure"
        return "churn_crisis"

    return "generic_analysis"

def run_benchmark(dataset_path: str, version: str = "v2", override_industry: str = None):
    print(f"\n🚀 Starting Universal Benchmark Suite ({version}) on {dataset_path}...")
    
    base_name = os.path.basename(dataset_path)
    dataset_name = os.path.splitext(base_name)[0]
    
    # 🎯 Dynamic Industry Mapping
    industry = override_industry if override_industry else "banking"
    
    # 🎯 Dynamic Scenario Routing
    scenario = get_scenario_from_filename(dataset_name, industry)
    print(f"🎯 Auto-Routed to: Industry=[{industry.upper()}] | Scenario=[{scenario.upper()}]")
    
    report_path = f"data/outputs/reports/AI_{industry.capitalize()}_{dataset_name}_Report.md"
    metadata_path = f"evaluation/benchmark_cases/{industry}/{scenario}/metadata.json"
    vocab_path = "evaluation/configs/industry_vocabulary.json"
    
    if not os.path.exists(report_path):
        print(f"❌ Benchmark failed: Report not found at {report_path}")
        return
        
    with open(report_path, "r", encoding="utf-8") as f:
        report_markdown = f.read()
        
    print("🧠 Running Evaluation Engine...")
    try:
        engine = EvaluationEngine(report_markdown, metadata_path, vocab_path)
        report = engine.run_evaluation()
    except FileNotFoundError:
        print(f"❌ Error: Metadata file missing! Run build_suite.py to generate {metadata_path}")
        return
    
    os.makedirs(f"evaluation/results/{version}", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    dashboard_path = "evaluation/results/dashboard.csv"
    file_exists = os.path.exists(dashboard_path)
    
    with open(dashboard_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # Added Scenario column
            writer.writerow([
                "Timestamp", "Evaluation_Version", "Industry", "Dataset", "Scenario",
                "Total_Score", "Max_Score", "Percentage", 
                "Behavioral", "Prioritization", "Traceability", 
                "Governance", "Readability", "Realism"
            ])
            
        writer.writerow([
            timestamp, version, industry, dataset_name, scenario,
            report["total_score"], report["max_score"], report["percentage"],
            report["dimensions"]["behavioral_intelligence"],
            report["dimensions"]["prioritization"],
            report["dimensions"]["recommendation_traceability"],
            report["dimensions"]["governance"],
            report["dimensions"]["executive_readability"],
            report["dimensions"]["industry_realism"]
        ])
        
    print(f"📊 Telemetry updated: {dashboard_path}")
    
    json_path = f"evaluation/results/{version}/{industry}_{scenario}_score_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print("✅ Benchmark Complete!")
    print(f"Total Score: {report['total_score']} / {report['max_score']} ({report['percentage']}%)")
