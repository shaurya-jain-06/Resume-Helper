# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any

class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str]

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str]
    class Config:
        orm_mode = True

class ResumeUploadResp(BaseModel):
    resume_id: int
    ats_score: float
    issues: Optional[List[str]]
    suggestions: Optional[List[str]]

class ImproveRequest(BaseModel):
    resume_id: int
    company_type: Optional[str]

