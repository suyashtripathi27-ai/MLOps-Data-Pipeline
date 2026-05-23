import re

def clean_report_text(text):
    """Strips robotic AI phrasing out of the final report."""
    replacements = {
        "The data shows ": "",
        "This metric indicates ": "",
        "It is important to note that ": "",
        "Based on the KPI ": "",
        "Based on the payload ": "",
        "As seen in the evidence ": ""
    }
    
    # Apply replacements (case-insensitive where possible)
    for old, new in replacements.items():
        text = text.replace(old, new)
        text = text.replace(old.lower(), new)
        
    # Clean up any weird double-spacing left behind
    text = text.replace("  ", " ")
    
    return enforce_paragraph_compression(text)

def enforce_paragraph_compression(text):
    """
    If a paragraph is over 100 words, it finds the nearest sentence 
    boundary near the middle and forces a line break.
    """
    paragraphs = text.split('\n\n')
    compressed_paragraphs = []
    
    for p in paragraphs:
        words = p.split()
        if len(words) > 100 and not p.startswith('#') and not p.startswith('|'):
            # Find all periods followed by a space
            sentences = p.split('. ')
            if len(sentences) > 1:
                midpoint = len(sentences) // 2
                part1 = '. '.join(sentences[:midpoint]) + '.'
                part2 = '. '.join(sentences[midpoint:])
                compressed_paragraphs.append(part1 + "\n\n" + part2)
                continue
        compressed_paragraphs.append(p)
        
    return '\n\n'.join(compressed_paragraphs)
