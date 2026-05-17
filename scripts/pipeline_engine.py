import os
import sys
import pandas as pd
from openai import OpenAI

print("🌐 Starting Universal Omni-Channel Pipeline (Business Research Edition)...")

or_key = os.getenv("OPENROUTER_API_KEY")
if not or_key:
    print("❌ ERROR: OPENROUTER_API_KEY missing! Did you add it to GitHub Secrets?")
    sys.exit(1)

# 1. INITIALIZE OPENROUTER CLIENT WITH HEADERS
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=or_key,
    default_headers={
        "HTTP-Referer": "https://github.com", 
        "X-Title": "MLOps Automated Pipeline" 
    }
)

raw_dir = 'data/raw/'
processed_dir = 'data/processed/'
os.makedirs(processed_dir, exist_ok=True)

# 2. FIND THE DATA
files = [f for f in os.listdir(raw_dir) if f != '.gitkeep' and not f.startswith('.')]
if not files:
    print("No data files found.")
    sys.exit(0)

latest_file = files[0]
file_path = os.path.join(raw_dir, latest_file)
file_ext = os.path.splitext(latest_file)[1].lower()

print(f"📥 Detected file: {latest_file} | Format: {file_ext}")

# ==========================================
# 3. DEEP DATA EXTRACTION (Fixes the .zip and data_payload errors)
# ==========================================
print("📊 Extracting statistical profile...")
data_payload = ""
try:
    if file_ext == '.csv':
        df = pd.read_csv(file_path)
    elif file_ext == '.zip':
        df = pd.read_csv(file_path, compression='zip') # Native zip reading!
    elif file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        print(f"⚠️ Non-tabular file: {file_ext}")
        sys.exit(1)

    data_shape = df.shape
    data_types = df.dtypes.to_string()
    data_stats = df.describe(include='all').to_string()
    data_head = df.head(3).to_string()
    
    data_payload = f"""
    Total Rows: {data_shape[0]} | Total Columns: {data_shape[1]}
    
    [COLUMN DATA TYPES]
    {data_types}
    
    [STATISTICAL SUMMARY]
    {data_stats}
    
    [SAMPLE DATA (First 3 Rows)]
    {data_head}
    """
except Exception as e:
    print(f"❌ Error reading data: {e}")
    sys.exit(1)


# ==========================================
# 4. THE BUSINESS RESEARCH & CONSULTING PROMPT
# ==========================================
prompt = f"""
You are an elite Business Researcher and Strategic Management Consultant. I have handed you a raw dataset named '{latest_file}'. 
Here is the statistical profile and schema:

{data_payload}

Apply a rigorous Business Research Methodology to this data. Do not just blindly describe the numbers. You must first deduce the real-world business problem hidden in these statistics, and then design an analysis to solve that specific problem. 

Format your response in beautiful Markdown, structured exactly like this:

### 🚨 1. Problem Identification (The "Why")
* **Industry & Operation:** What specific business operation generated this data?
* **The Core Business Problem:** Look at the maximum values, variances, and standard deviations. What is the likely operational pain point or inefficiency this company is suffering from right now? (e.g., "High variance in duration suggests a severe bottleneck").

### 🎯 2. Research Objectives
* Based on the business problem identified above, define the top 3 core research questions this analysis must answer to save the company time or money.

### 🧹 3. Data Diagnostics & Cleaning Strategy
* Look at the data types and missing values (NaNs). What specific data quality issues are hindering this research? 
* Prescribe the exact cleaning steps required (e.g., standardizing timestamps, mapping missing source/destination IDs, handling outliers) so the analysis can be trusted.

### 🔬 4. Targeted Business Analysis
* Do not run generic analysis. Outline the specific statistical tests, comparative splits, or predictive models needed to answer the Research Objectives. 
* Explicitly name the columns you would use as your Dependent and Independent variables to prove where the inefficiencies are coming from.

### 🚀 5. Strategic Action Plan
* Based on the statistical footprint of the data, provide 3 aggressive, actionable business decisions the C-Suite must make to resolve the core problem you identified. Frame this using high-level strategic management logic.
"""

# ==========================================
# 5. CALL THE AI VIA OPENROUTER
# ==========================================
print("🧠 Generating Deep Analysis Report...")
try:
    completion = client.chat.completions.create(
        model="openrouter/free", 
        messages=[
            {"role": "system", "content": "You are a highly analytical Business Researcher. You give actionable, data-driven insights."},
            {"role": "user", "content": prompt}
        ],
    )
    ai_text = completion.choices[0].message.content
except Exception as e:
    print(f"❌ API Call Failed: {e}")
    sys.exit(1)

# ==========================================
# 6. SAVE THE REPORT
# ==========================================
report_name = f"AI_Analysis_{os.path.splitext(latest_file)[0]}.md"
output_path = os.path.join(processed_dir, report_name)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(ai_text)

print(f"✅ Universal Analysis complete! Dynamic report saved to: {output_path}")
