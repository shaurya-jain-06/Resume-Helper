# Resume-Helper
resume_ai_mvp/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ app/
│  ├─ __init__.py
│  ├─ main.py                # FastAPI app + routes
│  ├─ auth.py                # Google OAuth helpers
│  ├─ models.py              # SQLAlchemy models
│  ├─ db.py                  # DB session
│  ├─ schemas.py             # Pydantic schemas
│  ├─ llm_client.py          # Gemini + OpenAI wrapper
│  ├─ resume_parser.py       # PDF/DOCX extractor & parsing helpers
│  ├─ ats.py                 # ATS scoring logic / cached prompts
│  ├─ enhancer.py            # Resume rewriting logic
│  ├─ interview.py           # Interview question generation
│  ├─ storage.py             # Google Drive uploader
│  ├─ payments.py            # Payment gateway wrapper (stub)
│  └─ utils.py               # helpers: file io, prompt utils
└─ migrations/                # (optional) Alembic if you want

# Resume AI MVP (FastAPI)

## What this does
- Upload resume (PDF/DOCX)
- Compute ATS score using LLM (Gemini primary, OpenAI fallback)
- If user pays, improve resume with LLM, upload to Google Drive, and generate interview questions.

## Quick start (dev)
1. Copy `.env.example` -> `.env` and fill keys.
2. Create Python env and install:
   ```bash
   pip install -r requirements.txt

