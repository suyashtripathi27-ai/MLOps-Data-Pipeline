import os
import requests
import time
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_not_exception_type
from openai import RateLimitError

def execute_with_fallback(clients, system_prompt, final_prompt):
    """Cascading router that falls back through free AI services with smart retries."""
    
    # Initialize with a safe default if everything fails
    final_response = "### ⚠️ Pipeline Alert: All AI services are currently unavailable."
    
    # 1. The Free-Tier Cascade Strategy
    # Order: Service Name -> Guaranteed Working Free Model
    cascade_strategy = [
        ("gemini", "gemini-2.5-flash"),
        ("groq", "llama-3.1-8b-instant"),
        ("openrouter", "meta-llama/llama-3-8b-instruct:free")
    ]
    
    # 🌟 SMART RETRY: Try twice, wait 2 seconds between tries. 
    # BUT if it's a RateLimitError, skip the retries and let it fail instantly.
    @retry(
        stop=stop_after_attempt(2), 
        wait=wait_fixed(2), 
        retry=retry_if_not_exception_type(RateLimitError)
    )
    def call_llm(name, client, model):
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.05
        )
        return completion.choices[0].message.content

    # 2. Execute the Cascade Loop
    for name, target_model in cascade_strategy:
        if name in clients:
            try:
                print(f"-> 🟢 Routing to {name.upper()}...")
                
                # Call the Tenacity-wrapped function
                final_response = call_llm(name, clients[name], target_model)
                return final_response # Success! Exit the cascade.
                
            except RateLimitError:
                print(f"  ⚠️ {name.upper()} Quota Exceeded. Failing over immediately...")
            except Exception as e:
                print(f"  ⚠️ {name.upper()} failed after retries (Error: {e}). Failing over...")

    # 3. Try Hugging Face (Requests-based) as the final backup
    hf_key = clients.get("huggingface")
    if hf_key:
        for attempt in range(2): 
            try:
                print(f"-> 🟢 Routing to HUGGINGFACE (Attempt {attempt + 1})...")
                headers = {"Authorization": f"Bearer {hf_key}"}
                url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
                res = requests.post(url, headers=headers, json={"inputs": f"{system_prompt}\n{final_prompt}"})
                
                if res.status_code == 200:
                    return res.json()[0]['generated_text']
                else:
                    print(f"  ⚠️ HuggingFace API Rejected (Code {res.status_code}): {res.text}")
                    break # Stop retrying on hard rejections
                    
            except requests.exceptions.ConnectionError:
                print("  ⚠️ Network glitch. Retrying Hugging Face...")
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️ HuggingFace failed: {e}")
                break # Stop on other unexpected errors
                
    # 4. Return the fallback alert if the entire internet broke
    return final_response
