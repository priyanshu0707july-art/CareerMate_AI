import pytest
from unittest.mock import patch, MagicMock
from app.services.interview_service import start_interview, evaluate_and_progress
from app.models import Interview, InterviewQuestion, InterviewAnswer, Evaluation, Resume, Job, User

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@patch("app.services.interview_service.llm_provider.generate_json")
@patch("app.services.interview_service.retrieve_context")
def test_start_interview(mock_retrieve, mock_llm, mock_db):
    # Setup mocks
    mock_resume = Resume(id=1, user_id=1, structured_data={"skills": ["Python"]})
    mock_job = Job(id=1, user_id=1, structured_data={"required_skills": ["Python"]})
    
    # Mock db.query().filter().first() returns
    def db_query_side_effect(model):
        q = MagicMock()
        if model == Resume:
            q.filter.return_value.first.return_value = mock_resume
        elif model == Job:
            q.filter.return_value.first.return_value = mock_job
        return q
        
    mock_db.query.side_effect = db_query_side_effect
    
    mock_retrieve.return_value = "Retrieved context"
    mock_llm.return_value = {"question": "What is Python?"}
    
    # Run
    interview = start_interview(mock_db, user_id=1, resume_id=1, job_id=1, category="Python")
    
    assert interview.status == "IN_PROGRESS"
    assert interview.difficulty == "Medium"
    assert mock_llm.called
    assert mock_db.add.called

@patch("app.services.interview_service.llm_provider.generate_json")
@patch("app.services.interview_service.retrieve_context")
def test_evaluate_and_progress_adaptive_difficulty(mock_retrieve, mock_llm, mock_db):
    # Setup mocks
    mock_interview = Interview(id=1, user_id=1, job_id=1, difficulty="Medium", status="IN_PROGRESS", questions=[])
    mock_question = InterviewQuestion(id=1, interview_id=1, question_text="What is Python?")
    
    def db_query_side_effect(model):
        q = MagicMock()
        if model == Interview:
            q.filter.return_value.first.return_value = mock_interview
        elif model == InterviewQuestion:
            q.filter.return_value.first.return_value = mock_question
        elif model == Resume:
            q.join.return_value.filter.return_value.first.return_value = Resume(structured_data={})
        elif model == Job:
            q.filter.return_value.first.return_value = Job(structured_data={})
        return q
        
    mock_db.query.side_effect = db_query_side_effect
    mock_retrieve.return_value = ""
    
    # Return a high score for evaluate, then a question for next question
    mock_llm.side_effect = [
        {
            "technical_accuracy": 9,
            "completeness": 9,
            "clarity": 9,
            "communication": 9,
            "strengths": [],
            "weaknesses": [],
            "missing_concepts": [],
            "recommended_topics": []
        },
        {"question": "Next harder question?"}
    ]
    
    res = evaluate_and_progress(mock_db, interview_id=1, question_id=1, answer_text="Python is...", user_id=1)
    
    # Average score is 9.0, so difficulty should increase from Medium -> Hard
    assert mock_interview.difficulty == "Hard"
    assert res["status"] == "IN_PROGRESS"
    assert res["next_question"] == "Next harder question?"
