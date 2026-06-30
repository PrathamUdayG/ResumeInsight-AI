"""
scoring.py - Deterministic ATS scoring module.

Calculates the ATS compatibility score using weighted deterministic metrics.
Does NOT rely on LLM for scoring — all scores are computed programmatically.
"""

import re
from typing import Dict, List, Any

from utils.constants import (
    ATS_WEIGHTS, WEAK_VERBS, ALL_STRONG_VERBS,
    QUANTIFICATION_INDICATORS, DEGREE_LEVELS,
)


def calculate_ats_score(
    resume_data: Dict[str, Any],
    keyword_results: Dict[str, Any],
    jd_text: str = "",
) -> Dict[str, Any]:
    """
    Calculate the overall ATS score using deterministic weighted metrics.
    
    Each component is scored 0-100, then combined using the configured weights.
    The final score is a weighted average, NOT an LLM opinion.
    
    Args:
        resume_data: Parsed resume dictionary from parser.py.
        keyword_results: Results from keyword_match.match_keywords().
        jd_text: Raw job description text.
    
    Returns:
        Dictionary with overall score, component scores, and detailed feedback.
    """
    text = resume_data.get("text", "")
    sections = resume_data.get("sections", {})
    
    # Calculate individual component scores
    scores = {}
    feedback = {}
    
    # 1. Keyword Match Score (30%)
    scores["keyword_match"] = keyword_results.get("match_percentage", 0)
    feedback["keyword_match"] = _keyword_feedback(keyword_results)
    
    # 2. Skill Match Score (20%)
    scores["skill_match"] = _calculate_skill_score(resume_data, jd_text)
    feedback["skill_match"] = _skill_feedback(scores["skill_match"])
    
    # 3. Experience Match Score (15%)
    scores["experience_match"] = _calculate_experience_score(sections, jd_text)
    feedback["experience_match"] = _experience_feedback(scores["experience_match"])
    
    # 4. Education Match Score (10%)
    scores["education_match"] = _calculate_education_score(sections, jd_text)
    feedback["education_match"] = _education_feedback(scores["education_match"])
    
    # 5. Formatting Score (5%)
    scores["formatting"] = _calculate_formatting_score(text, sections)
    feedback["formatting"] = _formatting_feedback(scores["formatting"], sections)
    
    # 6. Action Verbs Score (10%)
    scores["action_verbs"] = _calculate_action_verb_score(text)
    feedback["action_verbs"] = _action_verb_feedback(text)
    
    # 7. Quantified Achievements Score (10%)
    scores["quantified_achievements"] = _calculate_quantification_score(text)
    feedback["quantified_achievements"] = _quantification_feedback(text)
    
    # Calculate weighted overall score
    overall_score = sum(
        scores[component] * weight
        for component, weight in ATS_WEIGHTS.items()
    )
    
    # Determine grade
    grade = _score_to_grade(overall_score)
    
    return {
        "overall_score": round(overall_score, 1),
        "grade": grade,
        "component_scores": {k: round(v, 1) for k, v in scores.items()},
        "weights": ATS_WEIGHTS,
        "feedback": feedback,
        "suggestions": _generate_suggestions(scores, keyword_results),
    }


def _calculate_skill_score(resume_data: Dict, jd_text: str) -> float:
    """Score based on how many required skills the resume demonstrates."""
    resume_skills = set(s.lower() for s in resume_data.get("skills", []))
    
    if not jd_text:
        # Without a JD, score based on skill density
        return min(len(resume_skills) * 5, 100)
    
    # Extract skills from JD
    from core.keyword_match import extract_keywords
    jd_keywords = set(k.lower() for k in extract_keywords(jd_text))
    
    if not jd_keywords:
        return 70  # Default if no keywords extracted
    
    matched = resume_skills & jd_keywords
    return min((len(matched) / max(len(jd_keywords), 1)) * 100, 100)


def _calculate_experience_score(sections: Dict, jd_text: str) -> float:
    """Score based on experience section quality and relevance."""
    experience_text = sections.get("experience", "")
    
    if not experience_text:
        return 0
    
    score = 40  # Base score for having experience
    
    # Check for date ranges (indicates structured experience)
    date_patterns = [
        r'\d{4}\s*[-–]\s*(?:\d{4}|present|current)',
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{4}',
    ]
    for pattern in date_patterns:
        if re.search(pattern, experience_text, re.IGNORECASE):
            score += 15
            break
    
    # Check for company names / job titles (capitalized multi-word phrases)
    if re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', experience_text):
        score += 10
    
    # Check for bullet points (structured format)
    bullet_count = len(re.findall(r'[•\-\*]\s', experience_text))
    if bullet_count >= 3:
        score += 15
    elif bullet_count >= 1:
        score += 8
    
    # Check for relevance to JD
    if jd_text:
        jd_lower = jd_text.lower()
        exp_lower = experience_text.lower()
        common_words = set(jd_lower.split()) & set(exp_lower.split())
        relevance = len(common_words) / max(len(set(jd_lower.split())), 1)
        score += min(relevance * 50, 20)
    
    return min(score, 100)


def _calculate_education_score(sections: Dict, jd_text: str) -> float:
    """Score based on education section completeness and relevance."""
    education_text = sections.get("education", "")
    
    if not education_text:
        return 0
    
    score = 30  # Base score for having education
    edu_lower = education_text.lower()
    
    # Check for degree level
    for level, keywords in DEGREE_LEVELS.items():
        for kw in keywords:
            if kw in edu_lower:
                if level == "phd":
                    score += 30
                elif level == "masters":
                    score += 25
                elif level == "bachelors":
                    score += 20
                elif level == "associate":
                    score += 15
                else:
                    score += 10
                break
        else:
            continue
        break
    
    # Check for graduation year
    if re.search(r'20\d{2}', education_text):
        score += 10
    
    # Check for institution name
    if re.search(r'(?:university|college|institute|school)', edu_lower):
        score += 10
    
    # Check for GPA
    if re.search(r'(?:gpa|cgpa)\s*:?\s*\d', edu_lower):
        score += 10
    
    # Relevance to JD
    if jd_text:
        jd_lower = jd_text.lower()
        if any(field in jd_lower and field in edu_lower for field in 
               ['computer science', 'engineering', 'data science', 'mathematics', 'statistics', 'business']):
            score += 10
    
    return min(score, 100)


def _calculate_formatting_score(text: str, sections: Dict) -> float:
    """Score based on resume formatting quality."""
    score = 0
    
    # Check section presence
    important_sections = ['experience', 'skills', 'education']
    sections_present = sum(1 for s in important_sections if s in sections)
    score += sections_present * 15
    
    # Check for bullet points
    bullet_count = len(re.findall(r'[•\-\*]\s', text))
    if bullet_count >= 5:
        score += 15
    elif bullet_count >= 2:
        score += 8
    
    # Check for contact info
    from utils.helpers import extract_email, extract_phone
    if extract_email(text):
        score += 10
    if extract_phone(text):
        score += 5
    
    # Penalize very long or very short resumes
    word_count = len(text.split())
    if 200 <= word_count <= 1500:
        score += 10
    elif word_count < 100:
        score -= 10
    
    return max(min(score, 100), 0)


def _calculate_action_verb_score(text: str) -> float:
    """Score based on usage of strong action verbs vs weak verbs."""
    text_lower = text.lower()
    words = text_lower.split()
    
    weak_count = sum(1 for verb in WEAK_VERBS if verb in text_lower)
    strong_count = sum(1 for verb in ALL_STRONG_VERBS if verb in text_lower)
    
    total_verbs = weak_count + strong_count
    if total_verbs == 0:
        return 50  # Neutral if no action verbs detected
    
    strong_ratio = strong_count / total_verbs
    score = strong_ratio * 100
    
    # Bonus for variety of strong verbs
    if strong_count >= 5:
        score = min(score + 10, 100)
    
    return score


def _calculate_quantification_score(text: str) -> float:
    """Score based on presence of quantified achievements."""
    text_lower = text.lower()
    
    quant_count = 0
    for indicator in QUANTIFICATION_INDICATORS:
        if indicator in text_lower:
            quant_count += 1
    
    # Also check for numbers followed by common units
    number_patterns = re.findall(r'\d+[%+]|\$\d+|\d+\s*(?:users|customers|percent)', text_lower)
    quant_count += len(number_patterns)
    
    if quant_count >= 8:
        return 100
    elif quant_count >= 5:
        return 80
    elif quant_count >= 3:
        return 60
    elif quant_count >= 1:
        return 40
    else:
        return 10


def _score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


# ─────────────────────────── Feedback Generators ───────────────────────────

def _keyword_feedback(results: Dict) -> List[str]:
    feedback = []
    match_pct = results.get("match_percentage", 0)
    if match_pct >= 80:
        feedback.append("✅ Excellent keyword coverage!")
    elif match_pct >= 60:
        feedback.append("⚠️ Good keyword coverage, but some important keywords are missing.")
    else:
        feedback.append("❌ Low keyword match. Add more relevant keywords from the job description.")
    
    missing = results.get("high_priority_missing", [])
    if missing:
        feedback.append(f"🔑 High-priority missing keywords: {', '.join(missing[:10])}")
    
    return feedback


def _skill_feedback(score: float) -> List[str]:
    if score >= 80:
        return ["✅ Your skills align well with the requirements."]
    elif score >= 50:
        return ["⚠️ Partial skill match. Consider adding more relevant skills."]
    else:
        return ["❌ Significant skill gap. Review the job description and add matching skills."]


def _experience_feedback(score: float) -> List[str]:
    if score >= 80:
        return ["✅ Strong experience section with good structure."]
    elif score >= 50:
        return ["⚠️ Experience section needs improvement. Add dates, bullet points, and quantified achievements."]
    else:
        return ["❌ Experience section is weak or missing. Structure it with clear roles, dates, and accomplishments."]


def _education_feedback(score: float) -> List[str]:
    if score >= 70:
        return ["✅ Education section is well-documented."]
    elif score >= 40:
        return ["⚠️ Add more details to education (degree, year, institution, GPA)."]
    else:
        return ["❌ Education section needs significant improvement or is missing."]


def _formatting_feedback(score: float, sections: Dict) -> List[str]:
    feedback = []
    missing = []
    for s in ['experience', 'skills', 'education']:
        if s not in sections:
            missing.append(s.title())
    if missing:
        feedback.append(f"❌ Missing sections: {', '.join(missing)}")
    if score >= 70:
        feedback.append("✅ Resume formatting looks good.")
    else:
        feedback.append("⚠️ Improve formatting with clear sections and bullet points.")
    return feedback


def _action_verb_feedback(text: str) -> List[str]:
    text_lower = text.lower()
    weak_found = [v for v in WEAK_VERBS if v in text_lower]
    if weak_found:
        return [f"⚠️ Weak verbs detected: {', '.join(weak_found[:5])}. Replace with stronger action verbs."]
    return ["✅ Good use of action verbs!"]


def _quantification_feedback(text: str) -> List[str]:
    text_lower = text.lower()
    has_numbers = bool(re.search(r'\d+[%$]|\$\d+', text_lower))
    if has_numbers:
        return ["✅ Good use of quantified achievements."]
    return ["⚠️ Add measurable achievements (percentages, dollar amounts, user counts, etc.)"]


def _generate_suggestions(scores: Dict, keyword_results: Dict) -> List[str]:
    """Generate actionable improvement suggestions based on scores."""
    suggestions = []
    
    if scores.get("keyword_match", 0) < 70:
        missing = keyword_results.get("high_priority_missing", [])
        if missing:
            suggestions.append(
                f"Add these missing keywords to your resume: {', '.join(missing[:8])}"
            )
    
    if scores.get("action_verbs", 0) < 60:
        suggestions.append(
            "Replace weak verbs (worked, helped, responsible for) with strong action verbs "
            "(developed, optimized, architected, implemented)."
        )
    
    if scores.get("quantified_achievements", 0) < 60:
        suggestions.append(
            "Add quantified achievements with metrics (%, $, users, latency, accuracy)."
        )
    
    if scores.get("formatting", 0) < 60:
        suggestions.append(
            "Improve formatting: add clear section headings, use bullet points, "
            "and ensure contact information is visible."
        )
    
    if scores.get("experience_match", 0) < 60:
        suggestions.append(
            "Strengthen your experience section with clear dates, company names, "
            "job titles, and structured bullet points."
        )
    
    if scores.get("education_match", 0) < 50:
        suggestions.append(
            "Add details to education: degree type, field of study, institution, "
            "graduation year, and GPA if strong."
        )
    
    if scores.get("skill_match", 0) < 60:
        suggestions.append(
            "Add a dedicated Skills section listing technologies, tools, and "
            "frameworks mentioned in the job description."
        )
    
    if not suggestions:
        suggestions.append("Your resume looks strong! Minor tweaks can still help — consider tailoring it further for each application.")
    
    return suggestions
