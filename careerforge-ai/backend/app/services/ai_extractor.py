from fastapi import HTTPException, status
from app.schemas.processing import StructuredResume, StructuredJob
from app.services.llm_service import llm_provider, LLMException
from app.prompts import RESUME_ANALYSIS_PROMPT, JOB_ANALYSIS_PROMPT
import logging

logger = logging.getLogger(__name__)

def extract_resume_data(text: str) -> StructuredResume:
    prompt = RESUME_ANALYSIS_PROMPT.format(text=text)
    
    try:
        data = llm_provider.generate_json(prompt)
        return StructuredResume(**data)
    except LLMException as e:
        logger.error(f"LLM extraction failed for resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to map LLM response to schema for resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process the AI response into structured data."
        )

def extract_job_data(text: str) -> StructuredJob:
    prompt = JOB_ANALYSIS_PROMPT.format(text=text)
    
    try:
        data = llm_provider.generate_json(prompt)
        return StructuredJob(**data)
    except LLMException as e:
        logger.error(f"LLM extraction failed for job: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to map LLM response to schema for job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process the AI response into structured data."
        )
