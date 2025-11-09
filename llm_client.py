# app/llm_client.py
import os
import httpx
import json
from typing import Optional

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = os.getenv("GEMINI_ENDPOINT")  # e.g. https://api.generativeai.google/v1beta2/models/gemini-1-5-flash:generate
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class LLMClient:
    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.gemini_endpoint = GEMINI_ENDPOINT
        self.openai_key = OPENAI_API_KEY

    async def call_gemini(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        if not self.gemini_key or not self.gemini_endpoint:
            return None
        headers = {
            "Authorization": f"Bearer {self.gemini_key}",
            "Content-Type": "application/json",
        }
        # Simple request shape for text generation - adapt to Google Gen AI schema
        payload = {
            "prompt": prompt,
            "maxOutputTokens": max_tokens,
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                r = await client.post(self.gemini_endpoint, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                # parse according to actual returned schema
                text = None
                if "candidates" in data and data["candidates"]:
                    text = data["candidates"][0].get("content")
                elif "output" in data and isinstance(data["output"], str):
                    text = data["output"]
                else:
                    text = json.dumps(data)
                return text
            except Exception as e:
                print("gemini error", e)
                return None

    async def call_openai(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        if not self.openai_key:
            return None
        import openai
        openai.api_key = self.openai_key
        try:
            resp = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
                max_tokens=max_tokens,
                temperature=0.2
            )
            text = resp.choices[0].message.content
            return text
        except Exception as e:
            print("openai error", e)
            return None

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        # Try Gemini first
        text = await self.call_gemini(prompt, max_tokens=max_tokens)
        if text:
            return text
        text = await self.call_openai(prompt, max_tokens=max_tokens)
        if text:
            return text
        raise RuntimeError("No LLM provider responded")

