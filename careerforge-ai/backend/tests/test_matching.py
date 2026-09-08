import pytest
from app.services.matching_service import calculate_match_score

def test_empty_resume_and_job():
    res = calculate_match_score({}, {})
    assert res["overall_score"] == 100.0  # Empty job means 0 requirements, thus 100% matched
    assert len(res["details"]["matched_skills"]) == 0

def test_100_percent_match():
    resume = {
        "skills": ["Python", "FastAPI"],
        "projects": ["Built a REST API with Python and FastAPI"],
        "experience": ["3 years of Python and FastAPI"],
        "education": ["BSc CS"]
    }
    job = {
        "required_skills": ["Python"],
        "preferred_skills": ["FastAPI"],
        "technologies": ["REST API"],
        "responsibilities": ["Build APIs"],
        "education_requirements": ["BSc"],
        "experience_requirements": ["3 years"]
    }
    
    res = calculate_match_score(resume, job)
    
    assert res["overall_score"] >= 80.0
    assert "python" in res["details"]["matched_skills"]
    assert "fastapi" in res["details"]["matched_skills"]
    assert len(res["details"]["missing_skills"]) == 0

def test_0_percent_match():
    resume = {
        "skills": ["Java", "Spring"],
        "projects": ["Built a bank app in Java"],
        "experience": ["Worked with Spring Boot"],
        "education": []
    }
    job = {
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["Docker"],
        "technologies": ["Machine Learning"],
        "responsibilities": ["Train models"],
        "education_requirements": ["PhD"],
        "experience_requirements": ["5 years Python"]
    }
    
    res = calculate_match_score(resume, job)
    
    assert res["overall_score"] < 20.0
    assert len(res["details"]["matched_skills"]) == 0
    assert "python" in res["details"]["missing_skills"]

def test_partial_match_and_duplicates():
    resume = {
        "skills": ["ReactJS", "Node.js", "ReactJS"],
        "projects": [],
        "experience": [],
        "education": []
    }
    job = {
        "required_skills": ["React", "Node", "MongoDB"],
    }
    
    res = calculate_match_score(resume, job)
    
    # "React" is in "ReactJS", "Node" is in "Node.js" -> Partial matches
    assert "react" in res["details"]["partial_matches"]
    assert "node" in res["details"]["partial_matches"]
    assert "mongodb" in res["details"]["missing_skills"]
