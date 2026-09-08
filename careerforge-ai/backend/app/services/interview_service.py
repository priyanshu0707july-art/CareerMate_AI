import json
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Interview, InterviewQuestion, InterviewAnswer, Evaluation, Resume, Job, InterviewStatus
from app.services.llm_service import llm_provider, LLMException
from app.prompts.interviewer import INTERVIEWER_PROMPT
from app.prompts.evaluation import EVALUATION_PROMPT
from app.services.rag_service import retrieve_context
from app.schemas.ai import NextQuestion, AnswerEvaluation

logger = logging.getLogger(__name__)

def generate_single_question(db: Session, interview: Interview, resume: Resume, job: Job) -> InterviewQuestion:
    """Generates the next question for an interview, dynamically setting difficulty based on state."""
    
    # Get previous questions to avoid repetition
    previous_qs = [q.question_text for q in interview.questions]
    prev_qs_str = "\n".join([f"- {q}" for q in previous_qs]) if previous_qs else "None"
    
    # Try to fetch some context based on the job category/responsibilities (simple approach)
    context_query = f"Interview questions for {interview.category} {job.structured_data.get('responsibilities', [''])[0]}" if job and job.structured_data else "Interview questions"
    context = retrieve_context(db, interview.user_id, query=context_query, top_k=2)

    prompt = INTERVIEWER_PROMPT.format(
        difficulty=interview.difficulty,
        category=interview.category,
        previous_questions=prev_qs_str,
        resume_data=json.dumps(resume.structured_data) if resume.structured_data else "{}",
        job_data=json.dumps(job.structured_data) if job and job.structured_data else "{}",
        retrieved_context=context
    )
    
    try:
        data = llm_provider.generate_json(prompt)
        parsed = NextQuestion(**data)
        
        question = InterviewQuestion(
            interview_id=interview.id,
            question_text=parsed.question
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question
    except Exception as e:
        logger.error(f"Failed to generate next question: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate the next interview question.")

def start_interview(db: Session, user_id: int, resume_id: int, job_id: int, category: str = "General") -> Interview:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    interview = Interview(
        user_id=user_id,
        job_id=job_id,
        status=InterviewStatus.IN_PROGRESS,
        difficulty="Medium",
        category=category
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    # Generate the first question
    generate_single_question(db, interview, resume, job)
    
    return interview

def evaluate_and_progress(db: Session, interview_id: int, question_id: int, answer_text: str, user_id: int):
    """Submits an answer, evaluates it, adapts difficulty, and generates the next question."""
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == user_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id, InterviewQuestion.interview_id == interview.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    # Save answer
    answer = InterviewAnswer(
        interview_id=interview.id,
        question_id=question.id,
        answer_text=answer_text
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    
    # Evaluate
    context = retrieve_context(db, user_id, query=f"{question.question_text} {answer_text}", top_k=2)
    prompt = EVALUATION_PROMPT.format(
        question=question.question_text,
        answer=answer_text,
        retrieved_context=context
    )
    
    try:
        data = llm_provider.generate_json(prompt)
        parsed = AnswerEvaluation(**data)
        
        avg_score = (parsed.technical_accuracy + parsed.completeness + parsed.clarity + parsed.communication) / 4.0
        
        evaluation = Evaluation(
            answer_id=answer.id,
            technical_accuracy=parsed.technical_accuracy,
            completeness=parsed.completeness,
            clarity=parsed.clarity,
            communication=parsed.communication,
            score=avg_score,
            details={
                "strengths": parsed.strengths,
                "weaknesses": parsed.weaknesses,
                "missing_concepts": parsed.missing_concepts,
                "recommended_topics": parsed.recommended_topics
            }
        )
        db.add(evaluation)
        
        # Adaptive Difficulty Logic
        if avg_score > 8.0:
            if interview.difficulty == "Easy": interview.difficulty = "Medium"
            elif interview.difficulty == "Medium": interview.difficulty = "Hard"
        elif avg_score < 5.0:
            if interview.difficulty == "Hard": interview.difficulty = "Medium"
            elif interview.difficulty == "Medium": interview.difficulty = "Easy"
            
        db.commit()
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate the answer.")
        
    # Generate next question unless we've asked 5 questions (arbitrary limit for mock)
    if len(interview.questions) < 5:
        # We need the resume and job
        resume = db.query(Resume).join(Interview, Interview.user_id == Resume.user_id).filter(Interview.id == interview.id).first()
        job = db.query(Job).filter(Job.id == interview.job_id).first()
        next_q = generate_single_question(db, interview, resume, job)
        return {"evaluation": parsed, "next_question": next_q.question_text, "next_question_id": next_q.id, "status": "IN_PROGRESS"}
    else:
        interview.status = InterviewStatus.COMPLETED
        db.commit()
        return {"evaluation": parsed, "status": "COMPLETED"}
