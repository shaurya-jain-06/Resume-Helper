# app/utils.py
import os
import aiofiles
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    async with aiofiles.open(destination, "wb") as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return destination

def allowed_file(filename: str) -> bool:
    ext = filename.lower().split('.')[-1]
    return ext in ("pdf", "docx", "doc", "txt")

