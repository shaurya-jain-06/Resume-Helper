# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.sql import func
from .db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_filename = Column(String)
    drive_original_link = Column(String, nullable=True)
    drive_improved_link = Column(String, nullable=True)
    ats_score = Column(Float, nullable=True)
    issues = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    company_type = Column(String, nullable=True)
    questions = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    improved = Column(Boolean, default=False)

    user = relationship("User")

