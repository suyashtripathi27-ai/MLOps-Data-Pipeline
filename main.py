import os
import sys
from openai import OpenAI

# 1. IMPORT OUR UNIVERSAL UTILITIES
from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload
from tenacity import retry, stop_after_attempt, wait_exponential

# 2. SETUP GEMINI CLIENT (Via OpenAI Compatibility Layer)
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    print("❌ ERROR: GEMINI_API_KEY missing from environment variables.")
    sys.exit(1)

client = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_router_llm(client, prompt):
    """Calls Gemini API with automatic retries if rate limit is hit."""
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content.strip().lower()

def detect_industry(columns_list):
    """THE AGENTIC ROUTER: Looks at the column names and guesses the industry."""
    print(f"🔍 Sniffing data schema: {columns_list}")
   # ⚡ STEP 1: HEURISTIC FAST-TRACK (Saves API Quota)
    cols_str = str(columns_list).lower()
    
    if any(word in cols_str for word in ['store', 'dept', 'weekly_sales', 'retail']):
        print("🎯 Fast Route: Classified as [RETAIL] via Heuristics")
        return "retail"
    elif any(word in cols_str for word in ['hub', 'actual_time', 'fleet', 'osrm_time']):
        print("🎯 Fast Route: Classified as [LOGISTICS] via Heuristics")
        return "logistics"
    elif any(word in cols_str for word in ['account', 'balance', 'transaction', 'loan', 'deposit']):
        print("🎯 Fast Route: Classified as [BANKING] via Heuristics")
        return "banking"
    elif any(word in cols_str for word in ['batch', 'expiry', 'purity', 'therapeutic', 'drug', 'fda']):
        print("🎯 Fast Route: Classified as [PHARMA] via Heuristics")
        return "pharma"
        
    # 🧠 STEP 2: AI ROUTING (If heuristics fail to identify it)
    supported_industries = ["logistics", "retail", "banking", "pharma", "generic"]
    
    prompt = f"""
    Analyze these dataset columns: {columns_list}
    Classify the industry of this dataset. 
    You MUST reply with EXACTLY ONE WORD from this list in all lowercase: {supported_industries}.
    If it doesn't clearly match logistics, retail, or banking, reply with 'generic'.
    """
    
    try:
        # Calls the retry-wrapped function to prevent 429 crashes
        raw_response = call_router_llm(client, prompt)
        
        # Cleanup loop (Ensures we get a clean word even if AI adds a period)
        for valid_industry in supported_industries:
            if valid_industry in raw_response:
                print(f"🎯 AI Router Classified Industry As: [{valid_industry.upper()}]")
                return valid_industry
                
        return "generic"
        
    except Exception as e:
        print(f"⚠️ AI Routing failed (Rate Limit/Connection). Defaulting to generic. Error: {e}")
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
        industry = detect_industry(columns)
        print(f"🎯 Agentic Router Classified Industry As: [{industry.upper()}]")
        
        # --- D. PROFILE DATA & GENERATE PAYLOAD ---
        payload = generate_payload(df, industry_context=industry)
        
        # --- E. THE DYNAMIC SWITCHBOARD ---
        print(f"🔀 Routing to {industry} module...")
        
        if industry == "logistics":
            from industries.logistics.pipeline import run_logistics_analysis
            final_report = run_logistics_analysis(payload, client, df)

        elif industry == "retail":
            from industries.retail.pipeline import run_retail_analysis
            final_report = run_retail_analysis(payload, client, df)
            
        elif industry == "banking": 
            from industries.banking.pipeline import run_banking_analysis
            final_report = run_banking_analysis(payload, client, df)

        elif industry == "pharma": 
            from industries.pharma.pipeline import run_pharma_analysis
            final_report = run_pharma_analysis(payload, client, df)

        else:
            final_report = "Generic analysis simulated..."
            
        # --- F. SAVE OUTPUT ---
        # Append the original filename to the report name to avoid overwriting 
        # if multiple datasets are uploaded at the same time.
        base_name = os.path.splitext(file_name)[0]
        report_name = f"AI_{industry.capitalize()}_{base_name}_Report.md"
        output_path = os.path.join(output_dir, report_name)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_report)
            
        print(f"✅ Report saved to: {output_path}")

    # --- G. GRACEFUL EXIT ---
    if not processed_any_file:
        print("\n⏸️ No valid data files found in data/raw/. Pipeline sleeping safely.")

if __name__ == "__main__":
    main()
