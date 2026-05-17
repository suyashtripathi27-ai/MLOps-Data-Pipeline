import pandas as pd
import os
import sys
from google import genai

print("🚀 Starting Automated MLOps Pipeline...")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: API Key missing!")
    sys.exit(1)

# NEW: Using the modern Google GenAI Client
client = genai.Client(api_key=api_key)

raw_dir = 'data/raw/'
processed_dir = 'data/processed/'
os.makedirs(processed_dir, exist_ok=True)

files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
if not files:
    print("No CSV files found.")
    sys.exit(0)

latest_file = files[0]
file_path = os.path.join(raw_dir, latest_file)
print(f"📥 Reading file: {latest_file}")
df = pd.read_csv(file_path)

columns_str = ", ".join(df.columns.tolist())
prompt = f"Columns: {columns_str}. Does this belong to 'LOGISTICS' or 'RETAIL'? Reply with ONE WORD: LOGISTICS or RETAIL."

# NEW: Using the modern AI generation call and latest model
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=prompt
)

industry = response.text.strip().upper()
print(f"🤖 AI Classification: {industry}")

if "RETAIL" in industry:
    print("🛍️ Running Retail Analysis...")
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
    retail_summary = df.groupby('Day').agg({'Sales': 'sum'}).reset_index()
    output_path = os.path.join(processed_dir, 'retail_powerbi_ready.csv')
    retail_summary.to_csv(output_path, index=False)
    print("✅ Retail data saved!")
else:
    output_path = os.path.join(processed_dir, 'logistics_powerbi_ready.csv')
    df.to_csv(output_path, index=False)
    print("✅ Logistics data saved!")
