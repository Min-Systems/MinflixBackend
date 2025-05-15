def test_registration_success(client):
    """Test successful user registration."""
    response = client.post(
        "/registration",
        data={"username": "newuser@example.com", "password": "securepassword"}
    )
    
    assert response.status_code == 200
    # Verify response is a JWT token
    assert len(response.content) > 0
    
    # Optionally, verify token structure
    from app.core.jwt import verify_jwt_token
    token = response.content.decode()
    payload = verify_jwt_token(token)
    assert payload["id"] is not None
    assert len(payload["profiles"]) == 0  # New user has no profiles

def test_registration_duplicate_user(client, test_user):
    """Test registration with an existing username fails."""
    response = client.post(
        "/registration",
        data={"username": test_user.username, "password": "password123"}
    )
    
    assert response.status_code == 400
    assert "User already exists" in response.json()["detail"]

def test_login_success(client, test_user_data):
    """Test successful login."""
    response = client.post(
        "/login",
        data=test_user_data
    )
    
    assert response.status_code == 200
    # Verify response is a JWT token
    assert len(response.content) > 0
    
    # Optionally, verify token structure
    from app.core.jwt import verify_jwt_token
    token = response.content.decode()
    payload = verify_jwt_token(token)
    assert payload["id"] is not None

def test_login_invalid_password(client, test_user):
    """Test login with invalid password."""
    response = client.post(
        "/login",
        data={"username": test_user.username, "password": "wrongpassword"}
    )
    
    assert response.status_code == 404
    assert "Wrong Password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/login",
        data={"username": "nonexistent@example.com", "password": "anypassword"}
    )
    
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]
