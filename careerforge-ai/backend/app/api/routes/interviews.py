from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Interview
from app.utils.auth import get_current_user
from app.schemas.interviews import StartInterviewRequest, SubmitAnswerRequest, InterviewHistoryResponse
from app.services.interview_service import start_interview, evaluate_and_progress
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/start")
@limiter.limit("5/minute")
def api_start_interview(
    request: Request,
    req: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = start_interview(db, current_user.id, req.resume_id, req.job_id, req.category)
    # Return first question
    first_q = interview.questions[0]
    return {
        "interview_id": interview.id,
        "first_question_id": first_q.id,
        "first_question": first_q.question_text
    }

@router.post("/{interview_id}/answer")
@limiter.limit("10/minute")
def api_submit_answer(
    request: Request,
    interview_id: int,
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = evaluate_and_progress(db, interview_id, req.question_id, req.answer_text, current_user.id)
    return res

@router.get("/history", response_model=List[InterviewHistoryResponse])
def api_get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).all()
    return interviews
