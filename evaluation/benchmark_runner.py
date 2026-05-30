import os
import json
import csv
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
        raise ValueError(f"Unsupported file format for {file_path}. Please provide a CSV, ZIP, or Excel file.")

def update_dashboard(results_dir, run_data):
    """Appends the latest benchmark run to the developer telemetry dashboard."""
    dashboard_path = os.path.join(results_dir, "dashboard.csv")
    file_exists = os.path.isfile(dashboard_path)
    
    # Define the exact columns for our telemetry dashboard
    headers = [
        "Timestamp", "Version", "Industry", "Dataset", 
        "Total_Score", "Max_Score", "Percentage",
        "Behavioral", "Prioritization", "Governance", 
        "Readability", "Realism"
    ]
    
    # Flatten the score dictionary into a CSV row
    row = [
        run_data["timestamp"],
        run_data["version"],
        run_data.get("industry", "banking"),  # Defaulting to banking for now
        run_data["benchmark"],
        run_data["evaluation"]["total_score"],
        run_data["evaluation"]["max_score"],
        run_data["evaluation"]["percentage"],
        run_data["evaluation"]["dimensions"].get("behavioral_intelligence", 0),
        run_data["evaluation"]["dimensions"].get("prioritization", 0),
        run_data["evaluation"]["dimensions"].get("governance", 0),
        run_data["evaluation"]["dimensions"].get("executive_readability", 0),
        run_data["evaluation"]["dimensions"].get("industry_realism", 0)
    ]
    
    # Append the row (and create headers if the file is new)
    with open(dashboard_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)
        
    print(f"📊 Telemetry updated: {dashboard_path}")

def run_benchmark(dataset_path, version="v1"):
    print(f"🚀 Starting Benchmark Suite ({version}) on {dataset_path}...")
    
    behavior_path = "evaluation/benchmark_cases/banking/churn_crisis/benchmark_metadata.json"
    vocab_path = "evaluation/configs/industry_vocabulary.json"
    
    # We will save the dashboard at the root of the results folder
    results_dir = "evaluation/results"
    version_dir = os.path.join(results_dir, version)
    os.makedirs(version_dir, exist_ok=True)
    
    try:
        df = load_dataset(dataset_path)
    except FileNotFoundError:
        print(f"⚠️ Dataset not found at {dataset_path}")
        return

    print("⚙️ Running Production Pipeline...")
    consumer_filename = os.path.basename(dataset_path).split('.')[0]
    payload = {"dataset_name": consumer_filename}
    clients = {} 
    
    report_path = f"data/outputs/reports/AI_Banking_{consumer_filename}_Report.md"
    
    try:
        run_banking_analysis(payload, clients, df)
    except Exception as e:
        print(f"⚠️ Pipeline failed to run on consumer data: {e}")
        return
    
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_markdown = f.read()
    except FileNotFoundError:
        print(f"⚠️ Could not find the generated report at {report_path}")
        return

    print("🧠 Running Evaluation Engine...")
    evaluator = EvaluationEngine(report_markdown, behavior_path, vocab_path)
    score_report = evaluator.run_evaluation()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"{version_dir}/banking_score_{consumer_filename}_{timestamp}.json"
    
    final_output = {
        "timestamp": timestamp,
        "version": version,
        "industry": "banking",
        "benchmark": consumer_filename,
        "evaluation": score_report
    }
    
    # 1. Save detailed JSON for debugging
    with open(result_filename, "w") as f:
        json.dump(final_output, f, indent=4)
        
    # 2. Append to developer CSV dashboard
    update_dashboard(results_dir, final_output)
        
    print("\n✅ Benchmark Complete!")
    print(f"Total Score: {score_report['total_score']} / {score_report['max_score']} ({score_report['percentage']}%)")
    print(f"Detailed Results saved to: {result_filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
    else:
        custom_path = "data/raw/Banking Customer Chrun Predicator Dataset.zip"
    
    run_benchmark(dataset_path=custom_path)
