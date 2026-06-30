"""
keyword_match.py - Keyword extraction and matching module.

Compares resume keywords against job description keywords using
exact matching, fuzzy matching (RapidFuzz), and semantic matching.
"""

import re
from typing import List, Dict, Set, Tuple

from rapidfuzz import fuzz, process
from utils.constants import ALL_SKILLS, SEMANTIC_SKILL_GROUPS
from utils.helpers import normalize_skill


def extract_keywords(text: str) -> List[str]:
    """
    Extract meaningful keywords from text.
    
    Combines skill database matching with n-gram extraction
    to catch both known skills and domain-specific terms.
    """
    text_lower = text.lower()
    keywords = set()
    
    # Match against known skills database
    for skill in ALL_SKILLS:
        if len(skill) <= 2:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                keywords.add(skill)
        elif skill in text_lower:
            keywords.add(skill)
    
    # Extract capitalized terms (likely technologies/tools)
    cap_pattern = r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b'
    capitalized = re.findall(cap_pattern, text)
    for term in capitalized:
        normalized = term.lower().strip()
        if len(normalized) > 2 and normalized not in {'the', 'and', 'for', 'with', 'this', 'that', 'from'}:
            keywords.add(normalized)
    
    # Extract terms in common tech patterns (e.g., "React.js", "Node.js")
    tech_pattern = r'\b[A-Za-z]+\.?[A-Za-z]*(?:\.[a-z]+)?\b'
    techs = re.findall(tech_pattern, text)
    for tech in techs:
        if '.' in tech and len(tech) > 3:
            keywords.add(tech.lower())
    
    return sorted(list(keywords))


def match_keywords(
    resume_keywords: List[str],
    jd_keywords: List[str],
    fuzzy_threshold: int = 80,
) -> Dict[str, any]:
    """
    Match resume keywords against job description keywords.
    
    Uses three matching strategies:
    1. Exact match: Direct string comparison
    2. Fuzzy match: RapidFuzz for similar but not identical terms
    3. Semantic match: Group-based matching for related skills
    
    Args:
        resume_keywords: Keywords extracted from the resume.
        jd_keywords: Keywords extracted from the job description.
        fuzzy_threshold: Minimum fuzzy match score (0-100).
    
    Returns:
        Dictionary with matched, missing, and categorized keywords.
    """
    resume_set = {normalize_skill(k) for k in resume_keywords}
    jd_set = {normalize_skill(k) for k in jd_keywords}
    
    # 1. Exact matches
    exact_matches = resume_set & jd_set
    
    # 2. Fuzzy matches (for remaining unmatched JD keywords)
    remaining_jd = jd_set - exact_matches
    remaining_resume = resume_set - exact_matches
    
    fuzzy_matches = set()
    fuzzy_pairs = []
    
    for jd_kw in remaining_jd:
        if remaining_resume:
            match = process.extractOne(
                jd_kw,
                list(remaining_resume),
                scorer=fuzz.token_sort_ratio,
            )
            if match and match[1] >= fuzzy_threshold:
                fuzzy_matches.add(jd_kw)
                fuzzy_pairs.append((jd_kw, match[0], match[1]))
    
    # 3. Semantic matches
    still_remaining = remaining_jd - fuzzy_matches
    semantic_matches = set()
    
    for jd_kw in still_remaining:
        for group_name, group_skills in SEMANTIC_SKILL_GROUPS.items():
            if jd_kw in group_skills:
                # Check if any resume keyword is in the same semantic group
                for resume_kw in remaining_resume:
                    if resume_kw in group_skills:
                        semantic_matches.add(jd_kw)
                        break
    
    # Calculate missing keywords
    all_matched = exact_matches | fuzzy_matches | semantic_matches
    missing_keywords = jd_set - all_matched
    
    # Identify high-priority missing keywords (skills in our database)
    high_priority = {kw for kw in missing_keywords if kw in {normalize_skill(s) for s in ALL_SKILLS}}
    
    # Identify rare keywords (in JD but not common)
    common_words = {'experience', 'work', 'team', 'ability', 'strong', 'knowledge', 
                    'understanding', 'skills', 'years', 'required', 'preferred',
                    'excellent', 'good', 'working', 'including', 'related'}
    rare_keywords = {kw for kw in jd_set if kw not in common_words and len(kw) > 3}
    
    return {
        "matched_keywords": sorted(list(all_matched)),
        "exact_matches": sorted(list(exact_matches)),
        "fuzzy_matches": fuzzy_pairs,
        "semantic_matches": sorted(list(semantic_matches)),
        "missing_keywords": sorted(list(missing_keywords)),
        "high_priority_missing": sorted(list(high_priority)),
        "rare_keywords": sorted(list(rare_keywords)),
        "total_jd_keywords": len(jd_set),
        "total_resume_keywords": len(resume_set),
        "match_percentage": (len(all_matched) / len(jd_set) * 100) if jd_set else 0,
    }


def get_keyword_importance(keywords: List[str], text: str) -> List[Dict]:
    """
    Rank keywords by their frequency and position in the text.
    
    Keywords appearing more frequently and earlier in the text
    are considered more important.
    """
    text_lower = text.lower()
    results = []
    
    for keyword in keywords:
        kw_lower = keyword.lower()
        count = text_lower.count(kw_lower)
        first_pos = text_lower.find(kw_lower)
        
        # Importance score: frequency weighted by position
        position_weight = 1.0 - (first_pos / len(text_lower)) if first_pos >= 0 else 0
        importance = count * (1 + position_weight)
        
        results.append({
            "keyword": keyword,
            "frequency": count,
            "first_position": first_pos,
            "importance_score": round(importance, 2),
        })
    
    results.sort(key=lambda x: x["importance_score"], reverse=True)
    return results
