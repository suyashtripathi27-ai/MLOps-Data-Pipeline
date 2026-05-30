import os
import json
import pandas as pd
from datetime import datetime
from industries.banking.pipeline import run_banking_analysis
from evaluation.evaluation_engine import EvaluationEngine

def load_dataset(file_path):
    """Helper function to automatically use the correct pandas reader."""
    if file_path.endswith('.csv') or file_path.endswith('.zip'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV, ZIP, or Excel file.")

def run_benchmark(version="v1"):
    print(f"🚀 Starting Benchmark Suite ({version})...")
    
    # Define your active dataset path here! 
    # (Switch this string if you want to test CSV or Excel later)
    active_dataset_path = "data/raw/Banking Customer Chrun Predicator Dataset.zip"
    
    behavior_path = "evaluation/benchmark_cases/banking/churn_crisis/benchmark_metadata.json"
    vocab_path = "evaluation/configs/industry_vocabulary.json"
    results_dir = f"evaluation/results/{version}"
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        # Using our robust helper function
        df = load_dataset(active_dataset_path)
    except FileNotFoundError:
        print(f"⚠️ Dataset not found at {active_dataset_path}")
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
