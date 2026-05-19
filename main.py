import os
import sys
from openai import OpenAI

# 1. IMPORT OUR UNIVERSAL UTILITIES
from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload

# 2. SETUP OPENROUTER CLIENT
or_key = os.getenv("OPENROUTER_API_KEY")
if not or_key:
    print("❌ ERROR: OPENROUTER_API_KEY missing from environment variables.")
    sys.exit(1)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=or_key,
    default_headers={"HTTP-Referer": "https://github.com", "X-Title": "Universal AI Pipeline"}
)

def detect_industry(columns_list):
    """THE AGENTIC ROUTER: Looks at the column names and guesses the industry."""
    print(f"🔍 Sniffing data schema: {columns_list}")
    
    supported_industries = ["logistics", "retail", "generic"]
    
    prompt = f"""
    Analyze these dataset columns: {columns_list}
    Classify the industry of this dataset. 
    You MUST reply with EXACTLY ONE WORD from this list in all lowercase: {supported_industries}.
    If it doesn't clearly match logistics or retail, reply with 'generic'.
    """
    
    try:
        response = client.chat.completions.create(
            model="openrouter/free", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0 
        )
        detected = response.choices[0].message.content.strip().lower()
        
        if detected not in supported_industries:
            detected = "generic"
            
        return detected
    except Exception as e:
        print(f"⚠️ Industry detection failed. Defaulting to generic. Error: {e}")
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
        
        # --- D. GENERATE MATH PAYLOAD ---
        payload = generate_payload(df)
        
        # --- E. THE DYNAMIC SWITCHBOARD ---
        print(f"🔀 Routing to {industry} module...")
        
        if industry == "logistics":
            from industries.logistics.pipeline import run_logistics_analysis
            final_report = run_logistics_analysis(payload, client, df)
            
       elif industry == "retail":
            from industries.retail.pipeline import run_retail_analysis
            final_report = run_retail_analysis(payload, client, df)
            
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
