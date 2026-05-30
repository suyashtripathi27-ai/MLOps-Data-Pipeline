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
        raise ValueError(f"Unsupported file format for {file_path}. Please provide a CSV, ZIP, or Excel file.")

# 👇 Notice we added dataset_path as an argument here
def run_benchmark(dataset_path, version="v1"):
    print(f"🚀 Starting Benchmark Suite ({version}) on {dataset_path}...")
    
    behavior_path = "evaluation/benchmark_cases/banking/churn_crisis/benchmark_metadata.json"
    vocab_path = "evaluation/configs/industry_vocabulary.json"
    results_dir = f"evaluation/results/{version}"
    os.makedirs(results_dir, exist_ok=True)
    
    try:
        df = load_dataset(dataset_path)
    except FileNotFoundError:
        print(f"⚠️ Dataset not found at {dataset_path}")
        return

    print("⚙️ Running Production Pipeline...")
    # Extract the filename dynamically to use in the report name
    consumer_filename = os.path.basename(dataset_path).split('.')[0]
    payload = {"dataset_name": consumer_filename}
    clients = {} 
    
    # Run pipeline and intercept report dynamically
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
    result_filename = f"{results_dir}/banking_score_{consumer_filename}_{timestamp}.json"
    
    final_output = {
        "timestamp": timestamp,
        "version": version,
        "benchmark": consumer_filename,
        "evaluation": score_report
    }
    
    with open(result_filename, "w") as f:
        json.dump(final_output, f, indent=4)
        
    print("\n✅ Benchmark Complete!")
    print(f"Total Score: {score_report['total_score']} / {score_report['max_score']} ({score_report['percentage']}%)")
    print(f"Results saved to: {result_filename}")

# This allows running it directly from terminal if needed
if __name__ == "__main__":
    import sys
    # If the user provides a file in the terminal, use it. Otherwise, fallback to a default.
    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
    else:
        custom_path = "data/raw/Banking Customer Chrun Predicator Dataset.zip"
    
    run_benchmark(dataset_path=custom_path)
