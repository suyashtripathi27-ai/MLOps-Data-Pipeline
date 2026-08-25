# 0. BOOTSTRAPPER (MUST BE FIRST): Enforces path resolution & __init__.py generation
import bootstrap

import os
import sys
import importlib  
from openai import OpenAI

# 1. IMPORT UNIVERSAL UTILITIES
from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload
from utils.chart_engine import generate_industry_charts
from evaluation.benchmark_runner import run_benchmark

# 2. HIGH-AVAILABILITY CLIENT SETUP
print("🔌 Initializing Multi-API Client Router...")
clients = {}

gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    clients["gemini"] = OpenAI(
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    clients["groq"] = OpenAI(
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1"
    )

or_key = os.getenv("OPENROUTER_API_KEY")
if or_key:
    clients["openrouter"] = OpenAI(
        api_key=or_key,
        base_url="https://openrouter.ai/api/v1"
    )

hf_key = os.getenv("HUGGINGFACE_API_KEY")
if hf_key:
    clients["huggingface"] = hf_key

if not clients:
    print("❌ ERROR: No API keys found. Please set at least one API key.")
    sys.exit(1)

# Per-industry column-name signal library used for fully LOCAL, deterministic
# industry classification. No dataset values — only column NAMES — ever factor
# into this decision, and none of it is sent to any external API.
INDUSTRY_KEYWORDS = {
    "pharma":        ['fda', 'adverse_event', 'clinical', 'dosage', 'therapeutic', 'batch',
                       'yield', 'gmp', 'deviation', 'shelf_life', 'expiry', 'trial',
                       'regulatory', 'formulation', 'drug_class', 'active_ingredient'],
    "hr":            ['attrition', 'jobrole', 'maritalstatus', 'employee_id', 'tenure',
                       'engagement_score', 'headcount', 'recruitment', 'performance_rating',
                       'training_hours'],
    "ecommerce":     ['cart', 'checkout', 'pageview', 'session', 'conversion_rate',
                       'add_to_cart', 'bounce_rate', 'website', 'wishlist'],
    "manufacturing": ['downtime', 'oee', 'scrap', 'defect_rate', 'production_volume',
                       'machine_id', 'maintenance', 'throughput_rate', 'work_order'],
    "logistics":     ['demurrage', 'detention', 'freight', 'hub', 'osrm', 'route_id',
                       'fleet', 'sla', 'carrier', 'shipment_id', 'delivery_time'],
    "banking":       ['account_balance', 'loan', 'deposit', 'branch', 'interest_rate',
                       'credit_score', 'overdraft', 'npa', 'atm', 'ifsc', 'kyc'],
    "finance":       ['cashflow', 'ebitda', 'balance_sheet', 'expense_category',
                       'budget_variance', 'roi', 'npv', 'liquidity_ratio', 'gross_margin'],
    "retail":        ['store', 'boxes_shipped', 'sales_person', 'footfall', 'markdown',
                       'shrinkage', 'pos_terminal', 'sku', 'discount_pct', 'department'],
}

# Fallback signal set used only when NOTHING above matched at all — picks the
# safest general-purpose landing spot from broad table shape.
GENERIC_SALES_SIGNALS = ['product', 'revenue', 'amount', 'price', 'quantity',
                          'boxes', 'units', 'order', 'customer', 'sales']


def detect_industry(columns_list, file_name=""):
    """
    FULLY LOCAL, DETERMINISTIC INDUSTRY ROUTER.

    No AI call happens here, and no dataset values (row content) are ever
    inspected or transmitted for this decision — only the column NAMES already
    in memory. Every dataset that reaches this pipeline gets classified purely
    by this system's own logic, scored against a curated per-industry keyword
    library. Ties/near-misses fall back deterministically to the closest
    general-purpose industry rather than guessing.
    """
    print(f"🔍 Sniffing data schema locally: {columns_list}")
    cols_str = str(columns_list).lower()
    fname_str = str(file_name).lower()

    scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in cols_str)
        if industry in fname_str:
            score += 1  # small filename-hint tiebreaker
        scores[industry] = score

    best_industry = max(scores, key=scores.get)
    best_score = scores[best_industry]

    if best_score > 0:
        print(f"🎯 Classified as [{best_industry.upper()}] via local schema scoring "
              f"({best_score} operational column signal(s) matched)")
        return best_industry

    # No industry-specific operational evidence anywhere in the schema.
    # Fall back to the safest generic landing spot based on general table shape.
    if any(kw in cols_str for kw in ['cart', 'checkout', 'pageview']):
        print("🎯 No strong industry signal — defaulting to [ECOMMERCE] (cart/checkout shape)")
        return "ecommerce"
    if any(kw in cols_str for kw in GENERIC_SALES_SIGNALS):
        print("🎯 No strong industry signal — defaulting to [RETAIL] (generic sales/transaction shape)")
        return "retail"

    print("⚠️ No industry signal detected at all in the schema — defaulting to [FINANCE]")
    return "finance"

def is_valid_executive_report(report_text: str) -> bool:
    """Validates that a report is a full executive analysis and not a system error message."""
    if not report_text or len(report_text.strip()) < 300:
        return False
    if "System Error" in report_text or "Failed to process" in report_text:
        return False
    return True

def main():
    print("🚀 Starting Universal Enterprise Pipeline...")
    
    raw_dir = 'data/raw/'
    if not os.path.exists(raw_dir):
        print(f"❌ Error: Directory '{raw_dir}' not found.")
        sys.exit(1)

    output_dir = 'data/outputs/reports/'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('data/outputs/charts/', exist_ok=True)
    os.makedirs('data/outputs/logs/', exist_ok=True)

    processed_any_file = False

    for file_name in os.listdir(raw_dir):
        if file_name.startswith('.') or file_name.lower() == 'process':
            continue
            
        if not file_name.endswith(('.csv', '.zip', '.xls', '.xlsx')):
            continue

        file_path = os.path.join(raw_dir, file_name)
        print(f"\n🚀 Processing dataset: {file_name}")
        processed_any_file = True
        
        try:
            df = load_and_clean(file_path)
            df = universal_clean(df)
        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
            continue 
        
        columns = df.columns.tolist()
        
        # 🔒 ROUTING IS FULLY LOCAL — no data leaves the system for this step
        industry = detect_industry(columns, file_name)
        
        # 📊 Auto-Generate Charts & Embed Markdown
        chart_markdown = generate_industry_charts(df, industry, file_name)
        
        payload = generate_payload(df, industry_context=industry)
        payload["chart_markdown"] = chart_markdown
        
        print(f"🔀 Routing to {industry} module...")
        
        ROUTER_MAP = {
            "logistics":     ("industries.logistics.pipeline",     "run_logistics_analysis"),
            "retail":        ("industries.retail.pipeline",        "run_retail_analysis"),
            "banking":       ("industries.banking.pipeline",       "run_banking_analysis"),
            "pharma":        ("industries.pharma.pipeline",        "run_pharma_analysis"),
            "finance":       ("industries.finance.pipeline",       "run_finance_analysis"),
            "manufacturing": ("industries.manufacturing.pipeline", "run_manufacturing_analysis"),
            "ecommerce":     ("industries.ecommerce.pipeline",     "run_ecommerce_analysis"),
            "hr":            ("industries.hr.pipeline",            "run_hr_analysis")
        }

        if industry in ROUTER_MAP:
            mod_path, func_name = ROUTER_MAP[industry]
            try:
                module = importlib.import_module(mod_path)
                analysis_func = getattr(module, func_name)
                final_report = analysis_func(payload, clients, df)
            except Exception as e:
                print(f"❌ Failed to run pipeline for {industry}: {e}")
                log_file = f"data/outputs/logs/error_{os.path.splitext(file_name)[0]}.log"
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"Pipeline error for {industry}: {e}")
                continue 
        else:
            print(f"⚠️ Unmapped industry: {industry}. Skipping evaluation.")
            continue
            
        # Attach Chart Blocks to Markdown if not present
        if chart_markdown and chart_markdown not in final_report:
            if "# 2. Operational Risk Synthesis" in final_report:
                final_report = final_report.replace("# 2. Operational Risk Synthesis", f"{chart_markdown}\n# 2. Operational Risk Synthesis")
            else:
                final_report = final_report + f"\n\n{chart_markdown}"

        base_name = os.path.splitext(file_name)[0]
        report_name = f"AI_{industry.capitalize()}_{base_name}_Report.md"
        output_path = os.path.join(output_dir, report_name) 
        
        if is_valid_executive_report(final_report):
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(final_report)
                print(f"✅ Report saved to: {output_path}")
                
                # 🚀 V3 DYNAMIC EVALUATION TIER
                run_benchmark(dataset_path=file_path, version="v3", override_industry=industry)
                
            except Exception as e:
                print(f"❌ Failed to save report or run evaluation: {e}")
        else:
            print(f"⚠️ Generated report for {file_name} was invalid or incomplete. Skipping benchmark evaluation.")

    if not processed_any_file:
        print("\n⏸️ No valid data files found in data/raw/. Pipeline sleeping safely.")

if __name__ == "__main__":
    main()
