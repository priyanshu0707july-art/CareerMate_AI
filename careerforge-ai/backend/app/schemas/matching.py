from pydantic import BaseModel, Field
from typing import List

class MatchDetails(BaseModel):
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    partial_matches: List[str] = Field(default_factory=list)
    project_matches: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class MatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    overall_score: float
    details: MatchDetails

    class Config:
        from_attributes = True
