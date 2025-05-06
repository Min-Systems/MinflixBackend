import pytest
from jose import jwt
from datetime import datetime, timedelta

from app.core.jwt import create_jwt_token, verify_jwt_token
from app.core.config import Settings

@pytest.fixture
def jwt_test_data():
    """Fixture providing test data for JWT tests."""
    return {
        "id": 1,
        "username": "test@example.com",
        "profiles": [{"id": 1, "displayname": "Test Profile"}]
    }

@pytest.fixture
def valid_token(jwt_test_data):
    """Fixture providing a valid JWT token."""
    return create_jwt_token(jwt_test_data)

@pytest.fixture
def expired_token(jwt_test_data):
    """Fixture providing an expired JWT token."""
    settings = Settings()
    to_encode = jwt_test_data.copy()
    expire = datetime.now() - timedelta(minutes=1)  # Already expired
    to_encode.update({"exp": expire, "token_type": "bearer"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def test_create_jwt_token(jwt_test_data):
    """Test JWT token creation."""
    settings = Settings()
    token = create_jwt_token(jwt_test_data)
    
    # Decode without verification to check payload
    decoded = jwt.decode(
        token, 
        settings.secret_key, 
        algorithms=[settings.algorithm]
    )
    
    assert decoded["id"] == jwt_test_data["id"]
    assert decoded["username"] == jwt_test_data["username"]
    assert "exp" in decoded
    assert decoded["token_type"] == "bearer"

def test_verify_jwt_token(valid_token, jwt_test_data):
    """Test JWT token verification."""
    decoded = verify_jwt_token(valid_token)
    
    assert decoded["id"] == jwt_test_data["id"]
    assert decoded["username"] == jwt_test_data["username"]

def test_verify_invalid_token():
    """Test verification fails with invalid token."""
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException) as excinfo:
        verify_jwt_token("invalid.token.string")
    
    assert excinfo.value.status_code == 401

def test_verify_expired_token(expired_token):
    """Test verification fails with expired token."""
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException) as excinfo:
        verify_jwt_token(expired_token)
    
    assert excinfo.value.status_code == 401