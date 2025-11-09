# app/ats.py
from .llm_client import LLMClient
import json

llm = LLMClient()

ATS_PROMPT_TEMPLATE = """
You are an Applicant Tracking System simulator. Score the resume on a scale 0-100 using ATS-style checks: keyword presence, role alignment, achievements, formatting, and clarity.
Return JSON: {{
  "ats_score": <int>,
  "issues": ["list of weaknesses (short)"],
  "suggestions": ["short actionable suggestions"]
}}
Resume:
{resume_text}
"""

async def compute_ats(resume_text: str) -> dict:
    prompt = ATS_PROMPT_TEMPLATE.format(resume_text=resume_text[:4000])
    resp = await llm.generate(prompt, max_tokens=600)
    # Attempt to parse JSON from response
    try:
        # find first '{' to last '}' heuristic
        start = resp.find("{")
        end = resp.rfind("}")
        if start != -1 and end != -1:
            json_blob = resp[start:end+1]
            data = json.loads(json_blob)
            return data
    except Exception:
        pass
    # fallback simple parser
    return {"ats_score": 50, "issues": ["parsing-fallback"], "suggestions": ["Improve keywords", "Add metrics"]}

