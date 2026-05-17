import os

def run_logistics_analysis(payload, client):
    """
    Grabs the logistics prompt, injects the data payload, and calls the AI.
    """
    print("🚚 Initializing Logistics Analysis Module...")
    
    # 1. Read the text prompt from the SAME folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompt.txt")
    
    with open(prompt_path, "r", encoding="utf-8") as file:
        raw_prompt = file.read()
        
    # 2. Inject the math payload
    final_prompt = raw_prompt.format(data_payload=payload)
    
    # 3. Call the AI
    print("🧠 Requesting Strategic Route Optimization Insights...")
    response = client.chat.completions.create(
        model="openrouter/free", 
        messages=[
            {"role": "system", "content": "You are an elite supply chain consultant."},
            {"role": "user", "content": final_prompt}
        ],
    )
    
    return response.choices[0].message.content
