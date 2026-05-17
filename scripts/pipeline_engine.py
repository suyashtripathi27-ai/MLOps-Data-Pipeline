import os
import sys
import pandas as pd
from openai import OpenAI

print("🌐 Starting Universal Omni-Channel Pipeline (OpenRouter Edition)...")

or_key = os.getenv("OPENROUTER_API_KEY")
if not or_key:
    print("❌ ERROR: OPENROUTER_API_KEY missing! Did you add it to GitHub Secrets?")
    sys.exit(1)

# 1. INITIALIZE OPENROUTER CLIENT
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=or_key,
)

raw_dir = 'data/raw/'
processed_dir = 'data/processed/'
os.makedirs(processed_dir, exist_ok=True)

# 2. FIND AND READ THE DATA
files = [f for f in os.listdir(raw_dir) if f != '.gitkeep' and not f.startswith('.')]
if not files:
    print("No data files found.")
    sys.exit(0)

latest_file = files[0]
file_path = os.path.join(raw_dir, latest_file)
file_ext = os.path.splitext(latest_file)[1].lower()

print(f"📥 Detected file: {latest_file} | Format: {file_ext}")

data_preview = ""
try:
    if file_ext == '.csv':
        df = pd.read_csv(file_path)
        data_preview = df.head(15).to_string()
    elif file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
        data_preview = df.head(15).to_string()
    else:
        data_preview = f"[Non-tabular file format: {file_ext}]"
except Exception as e:
    print(f"⚠️ Could not read file natively: {e}")
    sys.exit(1)

# 3. BUILD THE PROMPT
prompt = f"""
I have received a new dataset named '{latest_file}'.
Here is a preview of the raw data:

{data_preview}

Please provide a comprehensive analysis. Format your response clearly.
1. INDUSTRY: Identify the exact industry or business domain this data belongs to.
2. DATA PROFILING: What exactly does this dataset represent?
3. TOP 3 KPIs: Based on these specific columns, what are the 3 most critical Key Performance Indicators (KPIs) a CEO should track?
4. EXECUTIVE SUMMARY: Write a brief, professional summary of the data structure.
"""

# 4. CALL ANY MODEL VIA OPENROUTER
print("🧠 Calling OpenRouter API to analyze the dataset...")
try:
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat:free", # <-- You can change this to any OpenRouter model!
        messages=[
            {"role": "system", "content": "You are a Principal Enterprise Data Analyst."},
            {"role": "user", "content": prompt}
        ],
    )
    ai_text = completion.choices[0].message.content
except Exception as e:
    print(f"❌ API Call Failed: {e}")
    sys.exit(1)

# 5. SAVE THE REPORT
report_name = f"AI_Analysis_{os.path.splitext(latest_file)[0]}.txt"
output_path = os.path.join(processed_dir, report_name)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(ai_text)

print(f"✅ Universal Analysis complete! Dynamic report saved to: {output_path}")
