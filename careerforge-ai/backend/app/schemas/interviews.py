from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class StartInterviewRequest(BaseModel):
    resume_id: int
    job_id: int
    category: str = "General"

class SubmitAnswerRequest(BaseModel):
    question_id: int
    answer_text: str

class InterviewHistoryResponse(BaseModel):
    id: int
    status: str
    difficulty: str
    category: str
    
    class Config:
        from_attributes = True
