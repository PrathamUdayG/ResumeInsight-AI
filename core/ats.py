"""
ats.py - High-level ATS analysis orchestrator.
"""

from typing import Dict, List, Any
from core.keyword_match import extract_keywords, match_keywords
from core.scoring import calculate_ats_score


def run_ats_analysis(resume_data: Dict[str, Any], jd_text: str) -> Dict[str, Any]:
    """Run the complete ATS analysis pipeline."""
    resume_text = resume_data.get("text", "")
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    keyword_results = match_keywords(resume_keywords, jd_keywords)
    ats_score = calculate_ats_score(resume_data, keyword_results, jd_text)

    return {
        "ats_score": ats_score,
        "keyword_analysis": keyword_results,
        "resume_keywords": resume_keywords,
        "jd_keywords": jd_keywords,
        "resume_info": {
            "contact": resume_data.get("contact_info", {}),
            "sections_found": list(resume_data.get("sections", {}).keys()),
            "skills_found": resume_data.get("skills", []),
            "page_count": resume_data.get("page_count", 0),
            "format": resume_data.get("format", "unknown"),
        },
    }


def compare_resumes(resumes: List[Dict[str, Any]], jd_text: str) -> List[Dict[str, Any]]:
    """Compare multiple resumes against the same JD, sorted by score."""
    results = []
    for resume_data in resumes:
        report = run_ats_analysis(resume_data, jd_text)
        report["filename"] = resume_data.get("filename", "Unknown")
        results.append(report)
    results.sort(key=lambda x: x["ats_score"]["overall_score"], reverse=True)
    return results


def get_match_summary(report: Dict[str, Any]) -> Dict[str, float]:
    """Extract match percentage summary for display."""
    ats = report.get("ats_score", {})
    cs = ats.get("component_scores", {})
    return {
        "Overall Match": ats.get("overall_score", 0),
        "Keyword Match": cs.get("keyword_match", 0),
        "Skill Match": cs.get("skill_match", 0),
        "Experience Match": cs.get("experience_match", 0),
        "Education Match": cs.get("education_match", 0),
    }
