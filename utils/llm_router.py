import pandas as pd
import os
import requests
os.makedirs("data/outputs/reports/", exist_ok=True)
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import RateLimitError

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=5))
def _call_gemini(client, system_prompt, user_prompt):
    """Attempt direct Google Gemini connection."""
    print("   -> 🟢 Routing to Primary: Google Gemini...")
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.05
    )
    return response.choices[0].message.content

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=2, min=2, max=5))
def _call_openrouter(client, system_prompt, user_prompt):
    """Attempt OpenRouter fallback connection."""
    print("   -> 🟠 Routing to Fallback: OpenRouter...")
    response = client.chat.completions.create(
        # You can use any free model here (e.g., google/gemini-2.5-flash:free or meta-llama/llama-3-8b-instruct:free)
        model="meta-llama/llama-3.1-8b-instruct:free", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.05
    )
    return response.choices[0].message.content

def execute_with_fallback(clients, system_prompt, final_prompt):
    # Initialize with a safe default
    final_response = "### ⚠️ Pipeline Alert: All AI services are currently unavailable."
    
    # 1. Try OpenAI-compatible clients (Gemini/OpenRouter)
    for name in ["gemini", "openrouter"]:
        if name in clients:
            try:
                print(f"-> 🟢 Routing to {name.upper()}...")
                client = clients[name]
                completion = client.chat.completions.create(
                    model="gemini-1.5-flash" if name == "gemini" else "gpt-4o",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": final_prompt}]
                )
                final_response = completion.choices[0].message.content
                return final_response # Success
            except Exception as e:
                print(f"⚠️ {name.upper()} failed: {e}")

    # 2. Try Hugging Face (Requests-based)
    hf_key = clients.get("huggingface")
    if hf_key:
        try:
            print("-> 🟢 Routing to HUGGINGFACE...")
            headers = {"Authorization": f"Bearer {hf_key}"}
            # Use the actual free inference URL structure
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            res = requests.post(url, headers=headers, json={"inputs": f"{system_prompt}\n{final_prompt}"})
            if res.status_code == 200:
                final_response = res.json()[0]['generated_text']
                return final_response
            else:
                print(f"⚠️ HuggingFace API Rejected (Code {res.status_code}): {res.text}")   
        except Exception as e:
            print(f"⚠️ HuggingFace failed: {e}")
            
    # Return the fallback if all services failed
    return final_response
