import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

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
        model="google/gemini-2.5-flash:free", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.05
    )
    return response.choices[0].message.content

def execute_with_fallback(clients, system_prompt, user_prompt):
    """
    The High-Availability Router.
    Tries Gemini first. If it rate-limits or crashes, seamlessly swaps to OpenRouter.
    """
    # 1. Try Primary (Gemini)
    if clients.get("gemini"):
        try:
            return _call_gemini(clients["gemini"], system_prompt, user_prompt)
        except Exception as e:
            print(f"   ⚠️ Primary API Failed ({e}). Initiating Fallback Protocol...")
            
    # 2. Try Secondary (OpenRouter)
    if clients.get("openrouter"):
        try:
            return _call_openrouter(clients["openrouter"], system_prompt, user_prompt)
        except Exception as e:
            print(f"   ⚠️ Secondary API Failed ({e}).")
            
    raise Exception("❌ ALL LLM APIs EXHAUSTED. Rate limits reached across all providers.")
