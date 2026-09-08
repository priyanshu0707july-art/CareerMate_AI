import pytest
from unittest.mock import patch, MagicMock
from app.schemas.processing import StructuredResume, StructuredJob
from io import BytesIO

@pytest.fixture
def auth_headers(client, test_user):
    res = client.post("/auth/login", json={"email": test_user.email, "password": "testpassword"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@patch("app.api.routes.resumes.extract_text_from_file")
@patch("app.api.routes.resumes.extract_resume_data")
def test_upload_resume_success(mock_ai, mock_parser, client, auth_headers):
    # Mock parser
    mock_parser.return_value = "Mocked PDF text"
    
    # Mock AI extractor
    mock_structured = StructuredResume(skills=["Python"], experience=["Developer"])
    mock_ai.return_value = mock_structured
    
    # Create fake file
    file_content = b"fake pdf content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    
    response = client.post("/resumes/upload", headers=auth_headers, files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["structured_data"]["skills"] == ["Python"]

@patch("app.api.routes.jobs.extract_job_data")
def test_create_job_success(mock_ai, client, auth_headers):
    # Mock AI extractor
    mock_structured = StructuredJob(required_skills=["Python"], responsibilities=["Code"])
    mock_ai.return_value = mock_structured
    
    payload = {
        "title": "Software Engineer",
        "description": "We need a Python developer to write code."
    }
    
    response = client.post("/jobs", headers=auth_headers, json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Software Engineer"
    assert data["structured_data"]["required_skills"] == ["Python"]

def test_upload_resume_unauthorized(client):
    file_content = b"fake pdf content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    response = client.post("/resumes/upload", files=files)
    assert response.status_code == 401

def test_create_job_unauthorized(client):
    response = client.post("/jobs", json={"title": "Test", "description": "Test"})
    assert response.status_code == 401
