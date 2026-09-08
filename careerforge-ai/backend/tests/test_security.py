import pytest
from app.models.models import User, Resume
import io

def test_resume_upload_mime_validation(client, test_user):
    # Get token for test_user
    res = client.post("/auth/login", json={"email": "test@example.com", "password": "testpassword"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test uploading a fake image (which is not PDF/DOCX)
    file_content = b"fake image content"
    files = {"file": ("malicious.exe", io.BytesIO(file_content), "application/x-msdownload")}
    
    res = client.post("/resumes/upload", headers=headers, files=files)
    assert res.status_code == 400
    assert "Invalid file type" in res.json()["detail"]

def test_bola_idor_prevention(client, db_session, test_user):
    # Create User 2
    client.post("/auth/register", json={"name": "User2", "email": "u2@test.com", "password": "pass"})
    res2 = client.post("/auth/login", json={"email": "u2@test.com", "password": "pass"})
    token2 = res2.json()["access_token"]

    # Manually inject a resume for User 1 into the DB
    r = Resume(user_id=test_user.id, filename="u1.pdf", content="text", structured_data={"skills":[]})
    db_session.add(r)
    db_session.commit()
    db_session.refresh(r)
    resume_id = r.id

    # User 2 tries to access User 1's resume via matching endpoint
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    res = client.post(f"/analysis/{resume_id}/999", headers=headers2)
    assert res.status_code == 404
    assert "Resume not found" in res.json()["detail"]

def test_rate_limiting(client):
    # Make multiple requests rapidly to trigger rate limiter
    for _ in range(12):
        res = client.post("/auth/login", json={"email": "spam@test.com", "password": "pass"})
    
    assert res.status_code == 429
    assert "Rate limit exceeded" in res.json()["error"]
