import os
import json

def generate_v3_system_prompt(industry: str) -> str:
    """
    3-Layer Compositional Prompt Engine:
    Layer 1: Universal System Prompt (utils/universal_system_prompt.txt)
    Layer 2: Industry-Specific Prompt (industries/{industry}/system_prompt.txt)
    Layer 3: Strict V3 Evaluation Constraints (Automated Vocabulary & Formatting)
    """
    industry = industry.lower()
    base_dir = os.getcwd()
    
    # ---------------------------------------------------------
    # 📜 LAYER 1: Load Universal Consultant Rules (Now in utils/)
    # ---------------------------------------------------------
    universal_path = os.path.join(base_dir, "utils", "universal_system_prompt.txt")
    try:
        with open(universal_path, "r", encoding="utf-8") as f:
            layer1_universal = f.read().strip()
    except FileNotFoundError:
        print(f"⚠️ Warning: Universal prompt not found at {universal_path}")
        layer1_universal = "You are a Senior Enterprise Strategy Consultant."

    # ---------------------------------------------------------
    # 📜 LAYER 2: Load Industry-Specific Reasoning
    # ---------------------------------------------------------
    industry_path = os.path.join(base_dir, "industries", industry, "system_prompt.txt")
    try:
        with open(industry_path, "r", encoding="utf-8") as f:
            layer2_industry = f.read().strip()
    except FileNotFoundError:
        print(f"⚠️ Warning: Industry prompt not found at {industry_path}")
        layer2_industry = f"Focus your analysis on {industry.upper()} operational metrics and risks."

    # ---------------------------------------------------------
    # 🤖 LAYER 3: The MLOps Evaluator Constraints (Automated)
    # ---------------------------------------------------------
    vocab_path = os.path.join(base_dir, "evaluation", "configs", "industry_vocabulary.json")
    try:
        with open(vocab_path, "r", encoding="utf-8") as f:
            vocab = json.load(f).get(industry, {"tier1": [], "tier2": []})
    except FileNotFoundError:
        vocab = {"tier1": [], "tier2": []}

    tier1_words = ", ".join(vocab.get("tier1", []))
    tier2_words = ", ".join(vocab.get("tier2", []))

    layer3_constraints = f"""
---
STRICT FORMATTING AND EVALUATION CONSTRAINTS:
To pass the MLOps evaluation engine, you MUST adhere to the following rules based on the data provided:

1. MANDATORY VOCABULARY (INDUSTRY REALISM)
You must natively weave the following terms into your analysis:
- Primary Terms: {tier1_words}
- Secondary Terms: {tier2_words}

2. STRICT STRUCTURAL FORMAT (READABILITY)
Your response MUST contain exactly these five sections, using these exact markdown headers:
# 1. Executive Summary
# 2. Operational Diagnostics
# 3. Risk Prioritization
# 4. Strategic Recommendations
# 5. Governance & Data Limitations

3. PRIORITIZATION LOGIC
In Section "# 3. Risk Prioritization", you must explicitly state the absolute primary risk facing the operation.

4. ACTIONABLE TRACEABILITY
In Section "# 4. Strategic Recommendations", you MUST use strong action verbs such as: 'investigate', 'analyze', 'review', 'root cause', 'strategy', 'optimize', 'improve', 'campaign', 'remediate', 'audit', or 'conduct'.

5. GOVERNANCE (CRITICAL)
In Section "# 5. Governance & Data Limitations", you MUST use words like 'excluded', 'unavailable', or 'missing data', and state that the data 'limits assessment' or could 'affect conclusions'. NEVER use absolute words like 'proves', 'guarantees', '100%', 'certainly', or 'definitely'.
"""

    # Combine all 3 layers into the ultimate prompt!
    master_prompt = f"{layer1_universal}\n\n{layer2_industry}\n\n{layer3_constraints}"
    
    return master_prompt
