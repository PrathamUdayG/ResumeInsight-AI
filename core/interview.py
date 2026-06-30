"""
interview.py - AI interview question generator.

Generates contextual interview questions based on resume content
using RAG-retrieved context for relevance.
"""

from typing import List, Dict, Any
from core.llm import generate_response, get_gemini_model
from core.prompts import INTERVIEW_QUESTIONS_PROMPT


def generate_interview_questions(
    context: str,
    skills: List[str] = None,
    model=None,
) -> str:
    """
    Generate interview questions based on resume context.
    
    Args:
        context: Retrieved resume sections/chunks.
        skills: List of candidate's skills.
        model: Pre-configured Gemini model (optional).
    
    Returns:
        Formatted string of interview questions with answer guides.
    """
    if skills:
        context += f"\n\nKey Skills: {', '.join(skills)}"
    
    prompt = INTERVIEW_QUESTIONS_PROMPT.format(context=context)
    response = generate_response(prompt, model=model)
    return response


def generate_project_questions(project_text: str, model=None) -> str:
    """Generate interview questions specific to a project."""
    prompt = f"""Based on this project description, generate 5 deep-dive interview questions:

Project:
{project_text}

For each question, explain:
- What the interviewer is testing
- Key points a strong answer should cover
"""
    return generate_response(prompt, model=model)


def generate_skill_questions(skills: List[str], level: str = "intermediate", model=None) -> str:
    """Generate skill-specific technical questions."""
    prompt = f"""Generate {len(skills)} technical interview questions for these skills at {level} level:

Skills: {', '.join(skills)}

For each question:
1. State the question clearly
2. Provide a brief answer outline
3. Note common mistakes candidates make
"""
    return generate_response(prompt, model=model)
