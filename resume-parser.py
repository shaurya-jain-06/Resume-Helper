# app/resume_parser.py
import pdfplumber
import docx
from typing import Optional
import textract

def extract_text_from_pdf(path: str) -> str:
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text)

def extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text(path: str) -> str:
    ext = path.split('.')[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(path)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(path)
    else:
        # fallback with textract
        try:
            return textract.process(path).decode("utf-8")
        except Exception:
            return ""

