from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Job, User
from app.schemas.processing import JobCreate, JobResponse
from app.utils.auth import get_current_user
from app.services.ai_extractor import extract_job_data

router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Use Gemini API to extract structured data
    structured_data = extract_job_data(job_data.description)
    
    # Save to database
    job = Job(
        user_id=current_user.id,
        title=job_data.title,
        description=job_data.description,
        structured_data=structured_data.dict()
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job

@router.get("/", response_model=List[JobResponse])
def get_user_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    jobs = db.query(Job).filter(Job.user_id == current_user.id).all()
    return jobs
