import os
import json
import csv
from datetime import datetime
from evaluation.evaluation_engine import EvaluationEngine

def run_benchmark(dataset_path: str, version: str = "v2"):
    print(f"\n🚀 Starting Benchmark Suite ({version}) on {dataset_path}...")
    
    # Extract name for paths
    base_name = os.path.basename(dataset_path)
    dataset_name = os.path.splitext(base_name)[0]
    industry = "banking" # Defaulting for this suite
    
    report_path = f"data/outputs/reports/AI_{industry.capitalize()}_{dataset_name}_Report.md"
    metadata_path = f"evaluation/benchmark_cases/{industry}/churn_crisis/metadata.json"
    vocab_path = "evaluation/configs/industry_vocabulary.json"
    
    if not os.path.exists(report_path):
        print(f"❌ Benchmark failed: Report not found at {report_path}")
        return
        
    with open(report_path, "r", encoding="utf-8") as f:
        report_markdown = f.read()

    print(f"🔍 DEBUG: Current Working Directory is: {os.getcwd()}")
    print(f"🔍 DEBUG: Does metadata path exist? {os.path.exists(metadata_path)}")
    print("🔍 DEBUG: Contents of evaluation/ folder:")
    os.system("ls -R evaluation/benchmark_cases/")
    
    print("🧠 Running Evaluation Engine...")
    engine = EvaluationEngine(report_markdown, metadata_path, vocab_path)
    report = engine.run_evaluation()
    
    # Setup results directory
    os.makedirs(f"evaluation/results/{version}", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 📈 V2: Writing to Dashboard CSV
    dashboard_path = "evaluation/results/dashboard.csv"
    file_exists = os.path.exists(dashboard_path)
    
    with open(dashboard_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # V2 Headers with Evaluation_Version and Traceability
            writer.writerow([
                "Timestamp", "Evaluation_Version", "Industry", "Dataset", 
                "Total_Score", "Max_Score", "Percentage", 
                "Behavioral", "Prioritization", "Traceability", 
                "Governance", "Readability", "Realism"
            ])
            
        writer.writerow([
            timestamp,
            version,
            industry,
            dataset_name,
            report["total_score"],
            report["max_score"],
            report["percentage"],
            report["dimensions"]["behavioral_intelligence"],
            report["dimensions"]["prioritization"],
            report["dimensions"]["recommendation_traceability"],
            report["dimensions"]["governance"],
            report["dimensions"]["executive_readability"],
            report["dimensions"]["industry_realism"]
        ])
        
    print(f"📊 Telemetry updated: {dashboard_path}")
    
    # Save detailed JSON
    json_path = f"evaluation/results/{version}/{industry}_score_{dataset_name}_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print("✅ Benchmark Complete!")
    print(f"Total Score: {report['total_score']} / {report['max_score']} ({report['percentage']}%)")
    print(f"Detailed Results saved to: {json_path}")
