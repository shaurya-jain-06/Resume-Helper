# app/main.py
import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .utils import allowed_file, save_upload_file, UPLOAD_DIR
from pathlib import Path
from .resume_parser import extract_text
from .ats import compute_ats
from .enhancer import improve_resume_text
from .interview import generate_questions
from .storage import upload_file_to_drive
from .payments import create_checkout_session, verify_payment
from .db import get_db
from . import models
from .schemas import ResumeUploadResp, ImproveRequest
import shutil
import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Resume AI MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 5))

@app.on_event("startup")
async def startup():
    # Create DB tables (simple approach for MVP)
    async with get_db().__anext__() as db:  # hacky but ok for startup
        async with db.bind.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)

@app.post("/upload-resume", response_model=ResumeUploadResp)
async def upload_resume(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    size = 0
    # save file
    uid = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{uid}_{file.filename}"
    await save_upload_file(file, dest)
    # parse
    text = extract_text(str(dest))
    # compute ATS
    ats_result = await compute_ats(text)
    ats_score = float(ats_result.get("ats_score", 50))
    # persist minimal resume row
    new_resume = models.Resume(
        original_filename=file.filename,
        ats_score=ats_score,
        issues=ats_result.get("issues", []),
        suggestions=ats_result.get("suggestions", [])
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)
    return ResumeUploadResp(
        resume_id=new_resume.id,
        ats_score=ats_score,
        issues=new_resume.issues,
        suggestions=new_resume.suggestions
    )

@app.post("/create-checkout")
async def create_checkout(body: ImproveRequest):
    # In production, ensure user is authenticated and owns resume
    amount = 199  # example
    session = create_checkout_session(user_id=1, amount=amount, resume_id=body.resume_id)
    return session

@app.post("/payment-verify")
async def payment_verify(payment_id: str, resume_id: int, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    status = verify_payment(payment_id)
    if status.get("status") != "SUCCESS":
        raise HTTPException(status_code=402, detail="Payment failed")
    # fetch resume and mark paid flow -> process improvement
    q = await db.execute(select(models.Resume).where(models.Resume.id == resume_id))
    resume = q.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, "resume not found")
    # find file on disk (very simplified: assumes upload exists)
    # In production store path in DB. For MVP we search uploads dir for matching filename
    # We'll pick the first matching file
    from pathlib import Path
    for p in Path("uploads").glob(f"*{resume.original_filename}"):
        text = extract_text(str(p))
        break
    else:
        text = ""
    # background improvement
    async def process_improvement(resume_obj, resume_text):
        improved_text = await improve_resume_text(resume_text)
        # save improved text to temp file
        tmp_path = Path("uploads") / f"improved_{resume_obj.id}.txt"
        tmp_path.write_text(improved_text, encoding="utf-8")
        # upload both original and improved to Drive
        try:
            drive_orig = upload_file_to_drive(str(p), resume_obj.original_filename)
            drive_improved = upload_file_to_drive(str(tmp_path), f"improved_{resume_obj.original_filename}.txt", mimetype="text/plain")
            resume_obj.drive_original_link = drive_orig
            resume_obj.drive_improved_link = drive_improved
            resume_obj.improved = True
        except Exception as e:
            print("drive upload error", e)
        # generate interview Qs
        from .interview import generate_questions
        qs = await generate_questions(resume_text, resume_obj.company_type or "generic")
        resume_obj.questions = qs
        # attempt to recompute ATS for improved resume
        try:
            new_ats = await compute_ats(improved_text)
            resume_obj.ats_score = float(new_ats.get("ats_score", resume_obj.ats_score))
        except Exception:
            pass
        # commit changes
        async with db.begin():
            db.add(resume_obj)
    # schedule
    background_tasks.add_task(process_improvement, resume, text)
    return {"status": "processing", "message": "Resume improvement queued. You will receive links soon."}

@app.get("/resume/{resume_id}")
async def get_resume(resume_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Resume).where(models.Resume.id == resume_id))
    r = q.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "not found")
    return {
        "id": r.id,
        "ats_score": r.ats_score,
        "drive_original_link": r.drive_original_link,
        "drive_improved_link": r.drive_improved_link,
        "questions": r.questions or {}
    }

