import json
from fastapi import HTTPException, status
from app.schemas.ai import InterviewQuestionGen, AnswerEvaluation, StudyPlanGen
from app.services.llm_service import llm_provider, LLMException
from app.prompts import INTERVIEWER_PROMPT, EVALUATION_PROMPT, STUDY_PLAN_PROMPT
import logging

logger = logging.getLogger(__name__)

def generate_interview_questions(resume_data: dict, job_data: dict, num_questions: int = 5, retrieved_context: str = "") -> InterviewQuestionGen:
    prompt = INTERVIEWER_PROMPT.format(
        num_questions=num_questions,
        resume_data=json.dumps(resume_data),
        job_data=json.dumps(job_data),
        retrieved_context=retrieved_context
    )
    
    try:
        data = llm_provider.generate_json(prompt)
        return InterviewQuestionGen(**data)
    except LLMException as e:
        logger.error(f"Failed to generate interview questions: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to map interview questions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process AI response.")

def evaluate_answer(question: str, answer: str, retrieved_context: str = "") -> AnswerEvaluation:
    prompt = EVALUATION_PROMPT.format(question=question, answer=answer, retrieved_context=retrieved_context)
    
    try:
        data = llm_provider.generate_json(prompt)
        return AnswerEvaluation(**data)
    except LLMException as e:
        logger.error(f"Failed to evaluate answer: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to map evaluation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process AI response.")

def generate_study_plan(resume_data: dict, job_data: dict, retrieved_context: str = "") -> StudyPlanGen:
    prompt = STUDY_PLAN_PROMPT.format(
        resume_data=json.dumps(resume_data),
        job_data=json.dumps(job_data),
        retrieved_context=retrieved_context
    )
    
    try:
        data = llm_provider.generate_json(prompt)
        return StudyPlanGen(**data)
    except LLMException as e:
        logger.error(f"Failed to generate study plan: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to map study plan: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process AI response.")
