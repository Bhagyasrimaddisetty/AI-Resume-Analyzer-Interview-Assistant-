"""
analyzer.py
Core LLM-powered resume analysis: ATS scoring, skill gap, feedback, interview Qs.
"""
from utils.llm_client import call_llm
from utils.keyword_extractor import compute_keyword_match


# ── Prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a senior technical recruiter and career coach with 10+ years of experience "
    "in ATS systems and technical hiring. Give honest, specific, actionable feedback. "
    "Do not be generic. Be direct."
)


def analyze_resume_vs_jd(resume_text: str, jd_text: str, provider: str = "gemini") -> dict:
    """
    Full LLM-powered resume analysis against a job description.
    Returns a structured dict with scores and feedback.
    """
    kw_result = compute_keyword_match(resume_text, jd_text)

    prompt = f"""
You are evaluating a candidate's resume against a job description for ATS and recruiter fit.

--- RESUME ---
{resume_text[:3000]}

--- JOB DESCRIPTION ---
{jd_text[:2000]}

--- KEYWORD ANALYSIS (pre-computed) ---
Matched keywords: {', '.join(kw_result['matched']) or 'None'}
Missing keywords: {', '.join(kw_result['missing']) or 'None'}
Keyword match score: {kw_result['match_score']}%

Provide a structured analysis with EXACTLY these sections:

## OVERALL ATS SCORE
Give a score out of 100 with a one-line rationale.

## STRENGTHS (3-5 bullet points)
What the resume does well for this role.

## SKILL GAPS (3-5 bullet points)
Critical missing skills or experiences for this specific JD.

## IMPROVEMENT SUGGESTIONS (4-6 bullet points)
Specific, actionable resume edits — bullet rewrites, missing sections, quantification gaps.

## SECTION-BY-SECTION REVIEW
Rate each section: Summary, Experience, Skills, Education, Projects (Good / Needs Work / Missing).

## RECRUITER VERDICT
2-3 sentences: Would a recruiter shortlist this resume? Why / why not?
"""

    llm_response = call_llm(prompt, system=SYSTEM_PROMPT, provider=provider)

    return {
        "llm_analysis": llm_response,
        "keyword_match": kw_result,
    }


def generate_interview_questions(resume_text: str, jd_text: str, provider: str = "gemini") -> str:
    """Generate role-specific interview questions based on resume + JD."""
    prompt = f"""
Based on this resume and job description, generate targeted interview questions.

--- RESUME (summary) ---
{resume_text[:2000]}

--- JOB DESCRIPTION ---
{jd_text[:1500]}

Generate EXACTLY:
1. 5 Technical Questions (role-specific, not generic)
2. 3 Behavioral Questions (STAR format prompts, tied to the JD's requirements)
3. 2 Project Deep-Dive Questions (based on projects visible in the resume)
4. 1 Culture/Team Fit Question

For each question, include a brief note on what the interviewer is probing for.
Format clearly with numbered questions under each category header.
"""
    return call_llm(prompt, system=SYSTEM_PROMPT, provider=provider)


def generate_optimized_summary(resume_text: str, jd_text: str, provider: str = "gemini") -> str:
    """Generate an ATS-optimized professional summary."""
    prompt = f"""
Write a 3-4 sentence professional summary for this candidate optimized for this specific job.

--- RESUME ---
{resume_text[:2000]}

--- TARGET JOB DESCRIPTION ---
{jd_text[:1500]}

Requirements:
- Include 4-6 keywords directly from the JD naturally
- Quantify impact where possible based on resume content
- Avoid buzzwords like "passionate", "dynamic", "results-driven"
- Write in first person without "I"
- Make it ATS-friendly and human-readable

Output ONLY the summary paragraph, nothing else.
"""
    return call_llm(prompt, system=SYSTEM_PROMPT, provider=provider)


def generate_cover_letter(resume_text: str, jd_text: str, company: str = "", provider: str = "gemini") -> str:
    """Generate a tailored cover letter."""
    prompt = f"""
Write a concise, compelling cover letter for this candidate applying to this role.

Company: {company or 'the company'}

--- RESUME ---
{resume_text[:2000]}

--- JOB DESCRIPTION ---
{jd_text[:1500]}

Requirements:
- 3 paragraphs: hook + value prop, evidence (2-3 specific achievements), closing
- Reference specific JD requirements with matching resume evidence
- No generic phrases like "I am writing to express my interest"
- Professional but not robotic
- 250-300 words max
"""
    return call_llm(prompt, system=SYSTEM_PROMPT, provider=provider)
