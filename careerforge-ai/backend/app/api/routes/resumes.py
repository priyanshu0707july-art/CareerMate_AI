from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Resume, User
from app.schemas.processing import ResumeResponse
from app.utils.auth import get_current_user
from app.services.file_parser import extract_text_from_file
from app.services.ai_extractor import extract_resume_data

router = APIRouter()

ALLOWED_MIME_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are allowed.")

    # Extract text from PDF or DOCX
    raw_text = extract_text_from_file(file)
    
    # Use Gemini API to extract structured data
    structured_data = extract_resume_data(raw_text)
    
    # Save to database
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        content=raw_text,
        structured_data=structured_data.dict()
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return resume

@router.get("/", response_model=List[ResumeResponse])
def get_user_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes
