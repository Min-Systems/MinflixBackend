# tests/test_routes/test_auth.py
import pytest
from fastapi import status

def test_registration(client):
    """Test basic user registration."""
    # Use a unique email to avoid conflicts
    import uuid
    unique_email = f"test-{uuid.uuid4()}@example.com"
    
    response = client.post(
        "/registration",
        data={"username": unique_email, "password": "testpassword"}
    )
    
    # Check response
    assert response.status_code == 200
    assert response.content  # Should contain a token

def test_login(client, test_user):
    """Test login with valid credentials."""
    test_user_data = {
        "username": test_user.username,
        "password": "testpassword"  
    }
    response = client.post(
        "/login",
        data=test_user_data
    )
    
    # Check response
    assert response.status_code == 200
    assert response.content  # Should contain a token

def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "/login",
        data={"username": test_user.username, "password": "wrongpassword"}
    )
    
    # Check error response
    assert response.status_code != 200
    data = response.json()
    assert "Wrong Password" in data["detail"]

def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/login",
        data={"username": "nonexistent@example.com", "password": "anypassword"}
    )
    
    # Check error response
    assert response.status_code != 200
    data = response.json()
    assert "User not found" in data["detail"]

def test_add_profile(client, test_user):
    """Test adding a profile."""
    # Mock the authentication
    from app.main import app
    from app.core.jwt import get_current_filmuser
    
    # Override the dependency
    app.dependency_overrides[get_current_filmuser] = lambda: test_user.id
    
    try:
        response = client.post(
            "/addprofile",
            data={"displayname": "Test Profile"}
        )
        
        # Check response
        assert response.status_code == 200
        assert response.content  # Should contain a token
    finally:
        # Clean up
        app.dependency_overrides.pop(get_current_filmuser)