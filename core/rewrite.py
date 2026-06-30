"""
rewrite.py - Bullet point rewriting module.

Uses the Gemini LLM to rewrite weak resume bullet points into
impactful, achievement-oriented statements.
"""

from typing import List, Dict
from core.llm import generate_response, get_gemini_model
from core.prompts import REWRITE_BULLET_PROMPT
from utils.constants import WEAK_VERBS


def rewrite_bullet(bullet_point: str, model=None) -> List[str]:
    """
    Rewrite a single bullet point into 3 improved versions.
    
    Args:
        bullet_point: The original bullet point text.
        model: Pre-configured Gemini model (optional).
    
    Returns:
        List of 3 improved bullet point versions.
    """
    prompt = REWRITE_BULLET_PROMPT.format(bullet_point=bullet_point)
    response = generate_response(prompt, model=model)
    
    # Parse numbered responses
    versions = []
    for line in response.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
            # Remove numbering/bullets
            cleaned = line.lstrip('0123456789.-•*) ').strip()
            if cleaned and len(cleaned) > 10:
                versions.append(cleaned)
    
    return versions[:3] if versions else [response.strip()]


def identify_weak_bullets(text: str) -> List[Dict]:
    """
    Identify bullet points that could be improved.
    
    Checks for weak verbs, lack of metrics, and vague language.
    """
    weak_bullets = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) < 10:
            continue
        
        # Check if it looks like a bullet point
        is_bullet = stripped[0] in '•-*–' or (len(stripped) > 0 and stripped[0].isupper())
        content = stripped.lstrip('•-*– ').strip()
        
        if not is_bullet or len(content.split()) < 3:
            continue
        
        reasons = []
        content_lower = content.lower()
        
        # Check for weak verbs
        for verb in WEAK_VERBS:
            if content_lower.startswith(verb) or f' {verb} ' in content_lower:
                reasons.append(f"Uses weak verb: '{verb}'")
                break
        
        # Check for lack of metrics
        import re
        has_metrics = bool(re.search(r'\d+[%$]|\$\d+|\d+\s*(?:users|customers|percent)', content_lower))
        if not has_metrics:
            reasons.append("No quantified metrics")
        
        # Check for vague language
        vague_words = ['various', 'several', 'many', 'some', 'good', 'great', 'nice']
        for word in vague_words:
            if word in content_lower:
                reasons.append(f"Vague language: '{word}'")
                break
        
        if reasons:
            weak_bullets.append({
                "line": i + 1,
                "text": content,
                "reasons": reasons,
            })
    
    return weak_bullets


def batch_rewrite(bullets: List[str], model=None) -> List[Dict]:
    """
    Rewrite multiple bullet points.
    
    Returns a list of dicts with original and improved versions.
    """
    if model is None:
        model = get_gemini_model()
    
    results = []
    for bullet in bullets:
        improved = rewrite_bullet(bullet, model=model)
        results.append({
            "original": bullet,
            "improved": improved,
        })
    
    return results
