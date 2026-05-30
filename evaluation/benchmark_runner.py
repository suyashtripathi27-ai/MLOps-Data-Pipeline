import os
import json
import pandas as pd
from datetime import datetime
from industries.banking.pipeline import run_banking_analysis
from evaluation.evaluation_engine import EvaluationEngine

def run_benchmark(version="v1"):
    print(f"🚀 Starting Benchmark Suite ({version})...")
    
    dataset_path_zip = "data/raw/Banking Customer Chrun Predicator Dataset.zip"
    dataset_path_csv = "data/raw/Banking Customer Chrun Predicator Dataset.csv"
    dataset_path_excel = "data/raw/Banking Customer Chrun Predicator Dataset.xlsx" # 👈 Pointing to your actual dataset!
    behavior_path = "evaluation/benchmark_cases/banking/churn_crisis/benchmark_metadata.json"
    vocab_path = "evaluation/configs/industry_vocabulary.json"
    results_dir = f"evaluation/results/{version}"
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"⚠️ Dataset not found at {dataset_path}")
        return

    print("⚙️ Running Production Pipeline...")
    payload = {"dataset_name": "churn_crisis_benchmark"}
    clients = {} 
    
    # Run pipeline and intercept report
    report_path = "data/outputs/reports/AI_banking_churn_crisis_benchmark_Report.md"
    run_banking_analysis(payload, clients, df)
    
    with open(report_path, "r", encoding="utf-8") as f:
        report_markdown = f.read()

    print("🧠 Running Evaluation Engine...")
    evaluator = EvaluationEngine(report_markdown, behavior_path, vocab_path)
    score_report = evaluator.run_evaluation()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"{results_dir}/banking_churn_score_{timestamp}.json"
    
    final_output = {
        "timestamp": timestamp,
        "version": version,
        "benchmark": "banking_churn_crisis",
        "evaluation": score_report
    }
    
    with open(result_filename, "w") as f:
        json.dump(final_output, f, indent=4)
        
    print("\n✅ Benchmark Complete!")
    print(f"Total Score: {score_report['total_score']} / {score_report['max_score']} ({score_report['percentage']}%)")
    print(f"Results saved to: {result_filename}")

if __name__ == "__main__":
    run_benchmark()
