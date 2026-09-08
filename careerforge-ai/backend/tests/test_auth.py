def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"name": "New User", "email": "new@example.com", "password": "newpassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["name"] == "New User"
    assert "id" in data

def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/auth/register",
        json={"name": "Another User", "email": test_user.email, "password": "password"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client, test_user):
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client, test_user):
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_protected_route_success(client, test_user):
    # First login
    login_res = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword"}
    )
    token = login_res.json()["access_token"]
    
    # Access protected route
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email

def test_protected_route_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
