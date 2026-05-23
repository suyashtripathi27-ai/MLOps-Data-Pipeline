import os
import sys
import importlib  
from openai import OpenAI

# 1. IMPORT OUR UNIVERSAL UTILITIES
from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload
from utils.llm_router import execute_with_fallback  # 🛡️ THE NEW FALLBACK ENGINE
from utils.contextual_matcher import detect_industry_from_columns

# 2. HIGH-AVAILABILITY CLIENT SETUP
print("🔌 Initializing Multi-API Client Router...")
clients = {}

gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    clients["gemini"] = OpenAI(
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
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
    print("❌ ERROR: No API keys found. Please set GEMINI_API_KEY or OPENROUTER_API_KEY.")
    sys.exit(1)


def detect_industry(clients, columns_list):
    """THE AGENTIC ROUTER: Looks at the column names and guesses the industry."""
    print(f"🔍 Sniffing data schema: {columns_list}")

    # ⚡ STEP 1: CONTEXTUAL ROUTING (Weighted context-aware matcher)
    routed_industry, routing_meta = detect_industry_from_columns(columns_list)
    if routed_industry:
        print(
            f"🎯 Context Route: Classified as [{routed_industry.upper()}] "
            f"(keywords={routing_meta.get('keyword_hits', [])}, context={routing_meta.get('context_hits', [])})"
        )
        return routed_industry
        
    # 🧠 STEP 2: AI ROUTING (If heuristics fail to identify it)
    supported_industries = ["logistics", "retail", "banking", "pharma", "manufacturing", "finance", "ecommerce", "generic"]
    system_prompt = "You are a data schema router. Follow instructions exactly."
    
    user_prompt = f"""
    Analyze these dataset columns: {columns_list}
    Classify the industry of this dataset. 
    You MUST reply with EXACTLY ONE WORD from this list in all lowercase: {supported_industries}.
    If it doesn't clearly match logistics, retail, banking, pharma, manufacturing, or finance, reply with 'generic'.
    """
    
    try:
        # 🛡️ Uses the new fallback router so industry detection never crashes!
        raw_response = execute_with_fallback(clients, system_prompt, user_prompt).strip().lower()
        
        # Cleanup loop (Ensures we get a clean word even if AI adds a period)
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

    # Make sure output directories exist before we start
    output_dir = 'data/outputs/reports/'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('data/outputs/charts/', exist_ok=True)
    os.makedirs('data/outputs/logs/', exist_ok=True)

    processed_any_file = False

    # --- A. LOOP & GUARDRAIL ---
    for file_name in os.listdir(raw_dir):
        
        # 🛡️ THE GUARDRAIL: Skip placeholders, hidden files, and unsupported formats
        if file_name.startswith('.') or file_name.lower() == 'process':
            print(f"⏭️ Skipping placeholder file: {file_name}")
            continue
            
        if not file_name.endswith(('.csv', '.zip', '.xls', '.xlsx')):
            print(f"⏭️ Skipping unsupported file type: {file_name}")
            continue

        file_path = os.path.join(raw_dir, file_name)
        print(f"\n🚀 Processing dataset: {file_name}")
        processed_any_file = True
        
        # --- B. INGEST & CLEAN ---
        try:
            df = load_and_clean(file_path)
            df = universal_clean(df)
        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
            continue # Skip to the next file if this one crashes
        
        # --- C. DETECT INDUSTRY ---
        columns = df.columns.tolist()
        industry = detect_industry(clients, columns)
        
        # --- D. PROFILE DATA & GENERATE PAYLOAD ---
        payload = generate_payload(df, industry_context=industry)
        
       # --- E. THE DYNAMIC SWITCHBOARD ---
        print(f"🔀 Routing to {industry} module...")
        
        ROUTER_MAP = {
            "logistics": ("industries.logistics.pipeline", "run_logistics_analysis"),
            "retail":    ("industries.retail.pipeline",    "run_retail_analysis"),
            "banking":   ("industries.banking.pipeline",   "run_banking_analysis"),
            "pharma":    ("industries.pharma.pipeline",    "run_pharma_analysis"),
            "finance":   ("industries.finance.pipeline",   "run_finance_analysis"),
            "manufacturing": ("industries.manufacturing.pipeline", "run_manufacturing_analysis"),
            "ecommerce": ("industries.ecommerce.pipeline", "run_ecommerce_analysis")
        }

        # Determine the report content
        if industry in ROUTER_MAP:
            mod_path, func_name = ROUTER_MAP[industry]
            module = importlib.import_module(mod_path)
            analysis_func = getattr(module, func_name)
            final_report = analysis_func(payload, clients, df)
        else:
            final_report = f"# Generic Analysis\n\nNo industry-specific pipeline detected for: {industry}."
            
        # --- F. SAVE OUTPUT ---
        base_name = os.path.splitext(file_name)[0]
        report_name = f"AI_{industry.capitalize()}_{base_name}_Report.md"
        output_path = os.path.join(output_dir, report_name) 
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_report)
            print(f"✅ Report saved to: {output_path}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            
    # --- G. GRACEFUL EXIT ---
    if not processed_any_file:
        print("\n⏸️ No valid data files found in data/raw/. Pipeline sleeping safely.")

if __name__ == "__main__":
    main()
