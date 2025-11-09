# app/enhancer.py
from .llm_client import LLMClient
llm = LLMClient()

ENHANCER_PROMPT = """
You are a professional resume optimizer. Keep facts unchanged but rewrite the resume to be ATS-friendly and aim for 95+ score.
Return the improved resume text only (no explanations).
Resume:
{resume_text}
"""

async def improve_resume_text(resume_text: str) -> str:
    prompt = ENHANCER_PROMPT.format(resume_text=resume_text[:7000])
    improved = await llm.generate(prompt, max_tokens=1500)
    return improved

