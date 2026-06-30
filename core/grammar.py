"""
grammar.py - Resume quality and grammar analysis module.

Detects weak bullet points, passive language, long sentences,
repeated words, weak action verbs, and missing metrics.
"""

import re
from typing import Dict, List, Any
from utils.constants import WEAK_VERBS, ALL_STRONG_VERBS, QUANTIFICATION_INDICATORS


def analyze_resume_quality(text: str, sections: Dict[str, str] = None) -> Dict[str, Any]:
    """Analyze resume text for quality issues and return detailed feedback."""
    if not text:
        return {"issues": [], "score": 0, "summary": "No text to analyze."}

    issues = []
    issues.extend(_detect_weak_bullets(text))
    issues.extend(_detect_passive_language(text))
    issues.extend(_detect_long_sentences(text))
    issues.extend(_detect_repeated_words(text))
    issues.extend(_detect_weak_verbs(text))
    issues.extend(_detect_missing_metrics(text))

    quality_score = max(0, 100 - len(issues) * 5)

    return {
        "issues": issues,
        "score": quality_score,
        "total_issues": len(issues),
        "summary": _quality_summary(quality_score, len(issues)),
    }


def _detect_weak_bullets(text: str) -> List[Dict]:
    """Detect bullet points that are too short or vague."""
    issues = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('•', '-', '*', '–')) or (len(stripped) > 0 and stripped[0].isupper()):
            content = re.sub(r'^[•\-\*–]\s*', '', stripped)
            if content and len(content.split()) < 4:
                issues.append({
                    "type": "weak_bullet",
                    "severity": "medium",
                    "line": i + 1,
                    "text": content,
                    "suggestion": f"Expand this bullet point: '{content}'. Add context, impact, and results.",
                })
    return issues[:10]


def _detect_passive_language(text: str) -> List[Dict]:
    """Detect passive voice patterns."""
    issues = []
    passive_patterns = [
        r'\b(?:was|were|been|being)\s+\w+ed\b',
        r'\b(?:is|are|was|were)\s+(?:being\s+)?\w+ed\b',
    ]
    for pattern in passive_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            context = text[max(0, match.start()-30):match.end()+30].strip()
            issues.append({
                "type": "passive_voice",
                "severity": "low",
                "text": match.group(),
                "context": context,
                "suggestion": "Rewrite using active voice for stronger impact.",
            })
    return issues[:8]


def _detect_long_sentences(text: str) -> List[Dict]:
    """Detect sentences that are too long for resume readability."""
    issues = []
    sentences = re.split(r'[.!?]+', text)
    for sent in sentences:
        words = sent.split()
        if len(words) > 30:
            issues.append({
                "type": "long_sentence",
                "severity": "medium",
                "text": sent.strip()[:100] + "...",
                "word_count": len(words),
                "suggestion": "Break this into shorter, more impactful bullet points (aim for 15-25 words).",
            })
    return issues[:5]


def _detect_repeated_words(text: str) -> List[Dict]:
    """Detect overused words in the resume."""
    issues = []
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    stop_words = {'with', 'that', 'this', 'from', 'have', 'been', 'were', 'they',
                  'their', 'will', 'would', 'could', 'should', 'also', 'more',
                  'than', 'into', 'over', 'about', 'which', 'when', 'what', 'your'}
    word_counts = {}
    for w in words:
        if w not in stop_words:
            word_counts[w] = word_counts.get(w, 0) + 1
    
    for word, count in sorted(word_counts.items(), key=lambda x: -x[1]):
        if count >= 5:
            issues.append({
                "type": "repeated_word",
                "severity": "low",
                "text": word,
                "count": count,
                "suggestion": f"'{word}' appears {count} times. Use synonyms for variety.",
            })
    return issues[:5]


def _detect_weak_verbs(text: str) -> List[Dict]:
    """Detect weak action verbs that should be replaced."""
    issues = []
    text_lower = text.lower()
    for verb in WEAK_VERBS:
        if verb in text_lower:
            replacements = ALL_STRONG_VERBS[:4]
            issues.append({
                "type": "weak_verb",
                "severity": "medium",
                "text": verb,
                "suggestion": f"Replace '{verb}' with stronger verbs like: {', '.join(replacements)}",
            })
    return issues


def _detect_missing_metrics(text: str) -> List[Dict]:
    """Check if the resume lacks quantified achievements."""
    issues = []
    text_lower = text.lower()
    quant_found = sum(1 for ind in QUANTIFICATION_INDICATORS if ind in text_lower)
    
    if quant_found < 3:
        issues.append({
            "type": "missing_metrics",
            "severity": "high",
            "text": "Few quantified achievements detected",
            "suggestion": "Add measurable results: percentages, dollar amounts, user counts, time saved, etc.",
        })
    return issues


def _quality_summary(score: int, issue_count: int) -> str:
    if score >= 80:
        return f"Excellent resume quality! Only {issue_count} minor issues found."
    elif score >= 60:
        return f"Good quality with room for improvement. {issue_count} issues detected."
    elif score >= 40:
        return f"Fair quality. {issue_count} issues need attention."
    else:
        return f"Resume needs significant improvement. {issue_count} issues found."
