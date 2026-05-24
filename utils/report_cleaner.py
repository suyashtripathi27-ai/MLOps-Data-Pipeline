import re

def clean_report_text(raw_text):
    """
    Polishes the LLM output by fixing broken Markdown, 
    removing trailing whitespace, and ensuring consistent spacing.
    """
    if not isinstance(raw_text, str):
        return str(raw_text)
        
    # 1. Remove excessive newlines (more than 2 become exactly 2)
    cleaned = re.sub(r'\n{3,}', '\n\n', raw_text)
    
    # 2. Ensure headers have a blank line above them for proper Markdown rendering
    cleaned = re.sub(r'([^\n])\n(#+ )', r'\1\n\n\2', cleaned)
    
    # 3. Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # 4. Remove hallucinated JSON blocks if the LLM accidentally output its thought process
    cleaned = re.sub(r'```json.*?```', '', cleaned, flags=re.DOTALL).strip()
    
    return cleaned
