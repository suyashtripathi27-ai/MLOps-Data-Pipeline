# 0. BOOTSTRAPPER (MUST BE FIRST): Enforces path resolution & __init__.py generation
import bootstrap

import os
import sys
import importlib  
from openai import OpenAI

# 1. IMPORT UNIVERSAL UTILITIES
from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload
from utils.llm_router import execute_with_fallback  
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

def detect_industry(clients, columns_list, file_name="", df=None):
    """
    THE AGENTIC ROUTER: Routes datasets dynamically based on column schema,
    file name hints, and a semantic peek at the actual row data.
    """
    print(f"🔍 Sniffing data schema: {columns_list}")
    cols_str = str(columns_list).lower()
    
    # ⚡ STEP 1: STRICT OVERRIDES BY COLUMNS ONLY (Saves API calls for obvious datasets)
    if any(word in cols_str for word in ['fda', 'adverse_event', 'clinical', 'dosage', 'therapeutic']):
        print("🎯 Fast Route: Classified as [PHARMA] via Schema Heuristics")
        return "pharma"
    if any(word in cols_str for word in ['attrition', 'jobrole', 'maritalstatus']):
        print("🎯 Fast Route: Classified as [HR] via Schema Heuristics")
        return "hr"
    if any(word in cols_str for word in ['cart', 'checkout', 'pageview', 'ecommerce']):
        print("🎯 Fast Route: Classified as [ECOMMERCE] via Schema Heuristics")
        return "ecommerce"
    if any(word in cols_str for word in ['downtime', 'oee', 'scrap', 'defect_rate', 'production_volume']):
        print("🎯 Fast Route: Classified as [MANUFACTURING] via Schema Heuristics")
        return "manufacturing"
    if any(word in cols_str for word in ['demurrage', 'detention', 'freight', 'hub', 'osrm']):
        print("🎯 Fast Route: Classified as [LOGISTICS] via Schema Heuristics")
        return "logistics"

    # 🧠 STEP 2: MULTI-API SEMANTIC ROUTING WITH ROW PEEKING
    print("-> 🟢 Routing to AI Schema Sniffer...")
    supported_industries = ["logistics", "retail", "banking", "pharma", "manufacturing", "finance", "ecommerce", "hr"]
    
    # 🛠️ THE FIX: Extract a small sample of the actual values to give the AI context
    sample_values = {}
    if df is not None and not df.empty:
        text_cols = df.select_dtypes(include=['object', 'string']).columns[:4]
        for col in text_cols:
            sample_values[col] = df[col].dropna().unique()[:3].tolist()
            
    system_prompt = "You are an Enterprise Data Schema Router. Follow instructions exactly."
    
    user_prompt = f"""
    Analyze the following dataset metadata:
    - Outer Filename: {file_name}
    - Columns: {columns_list}
    - Sample Row Values: {sample_values}
    
    Classify this dataset into EXACTLY ONE of the following 8 industries:
    [LOGISTICS, RETAIL, HR, BANKING, PHARMA, FINANCE, MANUFACTURING, ECOMMERCE]
    
    Respond with ONLY the exact industry name in brackets. Example: [PHARMA]

    Weigh SCHEMA/STRUCTURE more heavily than product-name semantics. A dataset with only
    transactional sales columns (date, product name, salesperson, quantity/boxes shipped,
    revenue, country/region) is a SALES/DISTRIBUTION dataset, even if the products happen to
    be medicines, drugs, or OTC items — classify that as [RETAIL], not [PHARMA].
    Only choose [PHARMA] if the columns themselves reflect pharma OPERATIONS: batch/lot
    tracking, manufacturing yield, out-of-spec/deviation rates, clinical trial enrollment,
    adverse events, regulatory submissions, or shelf-life/expiry monitoring at a batch level.
    If it is purely transactional/monetary with no domain-specific operational columns, prioritize [FINANCE].
    If it is a mix of production and supply chain, prioritize [MANUFACTURING].
    """
    
    try:
        raw_response = execute_with_fallback(clients, system_prompt, user_prompt).strip().lower()
        for valid_industry in supported_industries:
            if valid_industry in raw_response:
                candidate = valid_industry
                verified = _verify_operational_depth(candidate, cols_str, columns_list)
                if verified != candidate:
                    print(f"⚠️ AI classified [{candidate.upper()}] but no {candidate}-operational "
                          f"columns were found in the schema — overriding to [{verified.upper()}]")
                    return verified
                print(f"🎯 AI Router Classified Industry As: [{valid_industry.upper()}]")
                return valid_industry
        
        print("⚠️ AI Router returned ambiguous result. Defaulting to finance.")
        return "finance"
    except Exception as e:
        print(f"⚠️ AI Routing failed. Defaulting to finance. Error: {e}")
        return "finance"


# Industries whose analysis modules need deep, industry-specific OPERATIONAL columns
# to produce anything meaningful. Topical/semantic content (e.g. drug names, staff
# titles) is not enough evidence on its own — these keywords must appear in the
# actual COLUMN NAMES, not just sample values, or the classification is rejected.
OPERATIONAL_EVIDENCE = {
    "pharma":        ['fda', 'adverse_event', 'clinical', 'dosage', 'therapeutic',
                       'batch', 'yield', 'gmp', 'deviation', 'shelf_life', 'expiry',
                       'trial', 'regulatory', 'formulation'],
    "hr":            ['attrition', 'jobrole', 'maritalstatus', 'employee', 'tenure',
                       'engagement_score', 'headcount', 'recruitment'],
    "manufacturing": ['downtime', 'oee', 'scrap', 'defect_rate', 'production_volume',
                       'machine', 'maintenance', 'throughput_rate'],
    "logistics":     ['demurrage', 'detention', 'freight', 'hub', 'osrm', 'route',
                       'fleet', 'sla', 'carrier'],
    "banking":       ['account_balance', 'loan', 'deposit', 'branch', 'interest_rate',
                       'credit_score', 'overdraft', 'npa'],
}

# Where a rejected strict-industry guess should fall back to, based on a quick
# look at whether the schema still resembles a general sales/commerce table.
GENERIC_FALLBACK_SIGNALS = ['product', 'revenue', 'amount', 'price', 'quantity',
                             'boxes', 'units', 'order', 'customer', 'sales']


def _verify_operational_depth(candidate_industry, cols_str, columns_list):
    """
    Deterministic safety net that runs after the AI's classification.
    Prevents committing to an operationally-strict industry (pharma, manufacturing,
    banking, HR, logistics) purely because product names or job titles *sound* like
    that industry, when the schema itself has none of that industry's real
    operational columns. Falls back to RETAIL for generic sales-shaped data, or
    ECOMMERCE/FINANCE when that fits better, otherwise leaves the AI's answer as-is.
    """
    required_keywords = OPERATIONAL_EVIDENCE.get(candidate_industry)
    if required_keywords is None:
        return candidate_industry  # not a "strict" industry — trust the AI as-is

    if any(kw in cols_str for kw in required_keywords):
        return candidate_industry  # real operational evidence found — trust it

    # No operational evidence. Pick the safest generic landing spot.
    if any(kw in cols_str for kw in ['cart', 'checkout', 'pageview']):
        return "ecommerce"
    if any(kw in cols_str for kw in GENERIC_FALLBACK_SIGNALS):
        return "retail"
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
        
        # 🛠️ ROUTING IS NOW COMPLETELY AUTONOMOUS
        industry = detect_industry(clients, columns, file_name, df=df)
        
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
