# app/interview.py
from .llm_client import LLMClient
llm = LLMClient()

QUESTION_PROMPT = """
You are an interviewer for {company_type}. Given the resume below, generate:
- 10 technical questions (bullet list)
- 6 behavioral questions
Return JSON: {{ "technical": [...], "behavioral": [...] }}
Resume:
{resume_text}
"""

async def generate_questions(resume_text: str, company_type: str) -> dict:
    prompt = QUESTION_PROMPT.format(resume_text=resume_text[:7000], company_type=company_type or "generic tech company")
    resp = await llm.generate(prompt, max_tokens=800)
    import json
    try:
        start = resp.find("{")
        end = resp.rfind("}")
        if start != -1 and end != -1:
            return json.loads(resp[start:end+1])
    except Exception:
        pass
    # fallback
    return {"technical": ["Explain your top project."], "behavioral": ["Tell me about a time you failed."]}

