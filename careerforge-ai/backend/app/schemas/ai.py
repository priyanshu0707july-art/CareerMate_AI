from pydantic import BaseModel, Field
from typing import List

class InterviewQuestionGen(BaseModel):
    questions: List[str] = Field(default_factory=list)

class AnswerEvaluation(BaseModel):
    technical_accuracy: float = Field(ge=0, le=10)
    completeness: float = Field(ge=0, le=10)
    clarity: float = Field(ge=0, le=10)
    communication: float = Field(ge=0, le=10)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_concepts: List[str] = Field(default_factory=list)
    recommended_topics: List[str] = Field(default_factory=list)

class NextQuestion(BaseModel):
    question: str = ""

class StudyPlanGen(BaseModel):
    study_plan_markdown: str = ""
