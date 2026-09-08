from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Resume, Job, MatchResult, User
from app.schemas.matching import MatchResponse
from app.utils.auth import get_current_user
from app.services.matching_service import calculate_match_score
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/{resume_id}/{job_id}", response_model=MatchResponse)
@limiter.limit("10/minute")
def analyze_resume_job_match(
    request: Request,
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch Resume
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or does not belong to user")
        
    # Fetch Job
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or does not belong to user")

    # Guard against unparsed data
    if not resume.structured_data:
        raise HTTPException(status_code=400, detail="Resume has no structured data")
    if not job.structured_data:
        raise HTTPException(status_code=400, detail="Job has no structured data")

    # Calculate match
    match_dict = calculate_match_score(resume.structured_data, job.structured_data)

    # Save to database
    match_result = MatchResult(
        resume_id=resume.id,
        job_id=job.id,
        score=match_dict["overall_score"],
        details=match_dict["details"]
    )
    
    db.add(match_result)
    db.commit()
    db.refresh(match_result)
    
    return match_result
