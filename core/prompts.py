"""
prompts.py - All LLM prompt templates.

Centralized prompt management for consistent, hallucination-resistant
responses from Gemini.
"""

SYSTEM_PROMPT = """You are ResumeInsight AI, an expert career coach and resume consultant.
You provide actionable, specific advice based ONLY on the resume content provided.
Rules:
- Never invent achievements, metrics, or experiences the candidate hasn't mentioned.
- If suggesting metrics, explicitly say "consider adding" rather than fabricating numbers.
- Base all analysis on the provided context chunks.
- Be encouraging but honest about areas for improvement.
- Use bullet points for clarity."""

RAG_QA_PROMPT = """Based on the following resume sections, answer the user's question.
Use ONLY the information provided below. If the answer cannot be found in the context, say so.

Resume Context:
{context}

User Question: {question}

Provide a detailed, helpful answer:"""

REWRITE_BULLET_PROMPT = """Rewrite the following resume bullet point to be more impactful.
Rules:
- Use a strong action verb to start
- Add specificity and context
- If the original lacks metrics, suggest where metrics COULD be added (don't fabricate them)
- Keep it truthful to the original meaning
- Keep it concise (one line, 15-25 words)

Original: {bullet_point}

Provide 3 improved versions, numbered 1-3:"""

CAREER_SUGGESTIONS_PROMPT = """Based on the resume skills and the job description requirements below,
suggest specific improvements the candidate can make.

Resume Skills: {resume_skills}
Missing Skills: {missing_skills}
Job Description: {jd_summary}

Provide recommendations in these categories:
1. **Courses** - Specific courses or certifications to take
2. **Technologies** - Tools and frameworks to learn
3. **Projects** - Project ideas that would demonstrate missing skills
4. **Certifications** - Professional certifications to pursue

Be specific with course names, platforms, and project ideas:"""

INTERVIEW_QUESTIONS_PROMPT = """Generate interview questions based on this candidate's resume.

Resume Sections:
{context}

Generate 10 interview questions across these categories:
- **Technical Questions** (based on listed skills/technologies)
- **Project Questions** (about specific projects mentioned)
- **Behavioral Questions** (based on experience level)
- **System Design Questions** (if applicable)

For each question, provide a brief note on what a good answer should cover:"""

RESUME_IMPROVEMENT_PROMPT = """Analyze the following resume section and provide specific improvement suggestions.

Section: {section_name}
Content:
{section_content}

Job Description Context:
{jd_context}

Provide:
1. Strengths of this section
2. Specific weaknesses
3. Concrete rewrite suggestions (without fabricating achievements)
4. Missing elements that should be added:"""

SUMMARY_GENERATION_PROMPT = """Generate a professional summary for this candidate based on their resume.

Resume Content:
{context}

Target Role: {target_role}

Write a 3-4 sentence professional summary that:
- Highlights key strengths relevant to the target role
- Mentions years of experience (if apparent)
- Includes top skills and technologies
- Is written in first person
- Does NOT fabricate any information:"""
