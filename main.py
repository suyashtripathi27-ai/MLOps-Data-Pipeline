import os
import sys
import importlib  
from openai import OpenAI

# 1. IMPORT OUR UNIVERSAL UTILITIES
from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload
from utils.llm_router import execute_with_fallback  
from evaluation.benchmark_runner import run_benchmark # <-- 📈 Moved import to the top!

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

def detect_industry(clients, columns_list, file_name=""):
    """THE AGENTIC ROUTER: Intelligently routes datasets using strict overrides and weighted scoring."""
    lower_name = file_name.lower()
    
    # 🛡️ STEP 0: FILENAME SAFEGUARD (Prevents AI Column Hallucinations like "Status" -> "loan_status")
    if any(w in lower_name for w in ["logistics", "freight", "shipping"]): 
        print(f"🎯 Fast Route: Classified as [LOGISTICS] via Filename Override")
        return "logistics"
    if any(w in lower_name for w in ["hr", "attrition", "employee"]): 
        print(f"🎯 Fast Route: Classified as [HR] via Filename Override")
        return "hr"
    if any(w in lower_name for w in ["banking", "churn", "credit"]): 
        print(f"🎯 Fast Route: Classified as [BANKING] via Filename Override")
        return "banking"
    if any(w in lower_name for w in ["retail", "store"]): 
        print(f"🎯 Fast Route: Classified as [RETAIL] via Filename Override")
        return "retail"
    if any(w in lower_name for w in ["ecommerce", "cart"]): 
        print(f"🎯 Fast Route: Classified as [ECOMMERCE] via Filename Override")
        return "ecommerce"
    if any(w in lower_name for w in ["manufacturing", "production"]): 
        print(f"🎯 Fast Route: Classified as [MANUFACTURING] via Filename Override")
        return "manufacturing"
    if any(w in lower_name for w in ["finance", "liquidity"]): 
        print(f"🎯 Fast Route: Classified as [FINANCE] via Filename Override")
        return "finance"
    if any(w in lower_name for w in ["pharma", "clinical"]): 
        print(f"🎯 Fast Route: Classified as [PHARMA] via Filename Override")
        return "pharma"

    print(f"🔍 Sniffing data schema: {columns_list}")
    cols_str = str(columns_list).lower()
    
    # ⚡ STEP 1: STRICT OVERRIDES (The Silver Bullets)
    if any(word in cols_str for word in ['attrition', 'jobrole', 'maritalstatus', 'employee']):
        print("🎯 Fast Route: Classified as [HR] via Heuristics")
        return "hr"
        
    if any(word in cols_str for word in ['cart', 'checkout', 'pageview', 'ecommerce']):
        print("🎯 Fast Route: Classified as [ECOMMERCE] via Heuristics")
        return "ecommerce"
        
    if any(word in cols_str for word in ['fda', 'adverse_event', 'clinical', 'dosage', 'therapeutic']):
        print("🎯 Fast Route: Classified as [PHARMA] via Heuristics")
        return "pharma"
        
    if any(word in cols_str for word in ['downtime', 'oee', 'scrap']) or ('machine' in cols_str and 'defect' in cols_str):
        print("🎯 Fast Route: Classified as [MANUFACTURING] via Heuristics")
        return "manufacturing"

    if any(word in cols_str for word in ['demurrage', 'detention', 'freight', 'hub', 'osrm']):
        print("🎯 Fast Route: Classified as [LOGISTICS] via Heuristics")
        return "logistics"

    # ⚖️ STEP 2: WEIGHTED SCORING (For ambiguous datasets)
    scores = {
        "banking": sum(1 for k in ['loan', 'credit', 'mortgage', 'aml', 'kyc', 'overdraft', 'deposit', 'delinquency'] if k in cols_str),
        "finance": sum(1 for k in ['ebitda', 'cashflow', 'opex', 'cogs', 'liquidity', 'dividend', 'ledger', 'assets'] if k in cols_str),
        "retail": sum(1 for k in ['store', 'footfall', 'pos', 'markdown', 'shrinkage', 'register', 'shelf', 'retail'] if k in cols_str)
    }
    
    best_match = max(scores, key=scores.get)
    
    if scores[best_match] > 0:
        print(f"🎯 Fast Route: Classified as [{best_match.upper()}] via Weighted Score")
        return best_match
        
    # 🧠 STEP 3: AI ROUTING (If heuristics fail completely)
    supported_industries = ["logistics", "retail", "banking", "pharma", "manufacturing", "finance", "ecommerce", "hr", "generic"]
    system_prompt = "You are a data schema router. Follow instructions exactly."
    
    user_prompt = f"""
    Analyze these dataset columns: {columns_list}
    Classify the industry of this dataset. 
    You MUST reply with EXACTLY ONE WORD from this list in all lowercase: {supported_industries}.
    If it doesn't clearly match, reply with 'generic'.
    """
    
    try:
        raw_response = execute_with_fallback(clients, system_prompt, user_prompt).strip().lower()
        
        for valid_industry in supported_industries:
            if valid_industry in raw_response:
                print(f"🎯 AI Router Classified Industry As: [{valid_industry.upper()}]")
                return valid_industry
                
        return "generic"
        
    except Exception as e:
        print(f"⚠️ AI Routing failed (All APIs Exhausted). Defaulting to generic. Error: {e}")
        return "generic"
        

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
        industry = detect_industry(clients, columns, file_name) # 🛡️ Passed file_name here
        
        payload = generate_payload(df, industry_context=industry)
        
        print(f"🔀 Routing to {industry} module...")
        
        ROUTER_MAP = {
            "logistics":     ("industries.logistics.pipeline", "run_logistics_analysis"),
            "retail":        ("industries.retail.pipeline",    "run_retail_analysis"),
            "banking":       ("industries.banking.pipeline",   "run_banking_analysis"),
            "pharma":        ("industries.pharma.pipeline",    "run_pharma_analysis"),
            "finance":       ("industries.finance.pipeline",   "run_finance_analysis"),
            "manufacturing": ("industries.manufacturing.pipeline", "run_manufacturing_analysis"),
            "ecommerce":     ("industries.ecommerce.pipeline", "run_ecommerce_analysis"),
            "hr":            ("industries.hr.pipeline",        "run_hr_analysis")
        }

        if industry in ROUTER_MAP:
            mod_path, func_name = ROUTER_MAP[industry]
            try:
                module = importlib.import_module(mod_path)
                analysis_func = getattr(module, func_name)
                final_report = analysis_func(payload, clients, df)
            except Exception as e:
                print(f"❌ Failed to run pipeline for {industry}: {e}")
                final_report = f"# System Error\n\nFailed to process {industry} pipeline: {e}"
        else:
            final_report = f"# Generic Analysis\n\nNo industry-specific pipeline detected for: {industry}."
            
        base_name = os.path.splitext(file_name)[0]
        report_name = f"AI_{industry.capitalize()}_{base_name}_Report.md"
        output_path = os.path.join(output_dir, report_name) 
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_report)
            print(f"✅ Report saved to: {output_path}")
            
            # ==========================================
            # 🚀 V3 DYNAMIC EVALUATION TIER
            # ==========================================
            # It now dynamically grades whatever file it just processed!
            run_benchmark(dataset_path=file_path, version="v3", override_industry=industry)
            
        except Exception as e:
            print(f"❌ Failed to save report or run evaluation: {e}")
            
    if not processed_any_file:
        print("\n⏸️ No valid data files found in data/raw/. Pipeline sleeping safely.")

if __name__ == "__main__":
    main()
