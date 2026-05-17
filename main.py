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
    """
    THE AGENTIC ROUTER: Looks at the column names and guesses the industry.
    """
    print(f"🔍 Sniffing data schema: {columns_list[:5]}...")
    
    # As you add more industries, just add them to this list!
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
            temperature=0.0 # Keep it strict and deterministic
        )
        detected = response.choices[0].message.content.strip().lower()
        
        # Safety check: ensure the AI actually picked a supported industry
        if detected not in supported_industries:
            detected = "generic"
            
        return detected
    except Exception as e:
        print(f"⚠️ Industry detection failed. Defaulting to generic. Error: {e}")
        return "generic"

def main():
    print("🚀 Starting Universal Enterprise Pipeline...")
    
    # --- A. FIND THE FILE ---
    raw_dir = 'data/raw/'
    files = [f for f in os.listdir(raw_dir) if f != '.gitkeep' and not f.startswith('.')]
    if not files:
        print("⏸️ No data files found in data/raw/. Pipeline sleeping.")
        sys.exit(0)
    
    latest_file = files[0]
    file_path = os.path.join(raw_dir, latest_file)
    
    # --- B. INGEST & CLEAN (Using utils/) ---
    # 1. Ingest the file (CSV, ZIP, Excel)
    df = load_and_clean(file_path)
    # 2. Run the universal Data Engineering layer (medians, dupes, dates)
    df = universal_clean(df)
    
    # --- C. DETECT INDUSTRY ---
    columns = df.columns.tolist()
    industry = detect_industry(columns)
    print(f"🎯 Agentic Router Classified Industry As: [{industry.upper()}]")
    
    # --- D. GENERATE MATH PAYLOAD ---
    payload = generate_payload(df)
    
    # --- E. THE DYNAMIC SWITCHBOARD ---
    print(f"🔀 Routing to {industry} module...")
    
    if industry == "logistics":
        # UPDATED TO USE pipeline
        from industries.logistics.pipeline import run_logistics_analysis
        final_report = run_logistics_analysis(payload, client, df)
        
    elif industry == "retail":
        print("Retail module under construction. Using generic fallback.")
        final_report = "Retail analysis simulated..."
        
    else:
        final_report = "Generic analysis simulated..."
        
    # --- F. SAVE OUTPUT ---
    # UPDATED FOLDER STRUCTURE
    output_dir = 'data/outputs/reports/'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('data/outputs/charts/', exist_ok=True)
    os.makedirs('data/outputs/logs/', exist_ok=True)
    
    report_name = f"AI_{industry.capitalize()}_Report.md"
    output_path = os.path.join(output_dir, report_name)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_report)
