import pytest
from app.models.search_models import *

def test_search_response_model():
    """Test creating a SearchResponseModel."""
    search_response = SearchResponseModel(
        results=[1, 2, 3],
        token="jwt_token_string"
    )
    
    assert search_response.results == [1, 2, 3]
    assert search_response.token == "jwt_token_string"

def test_search_response_model_serialization():
    """Test serializing a SearchResponseModel to JSON."""
    search_response = SearchResponseModel(
        results=[1, 2, 3],
        token="jwt_token_string"
    )
    
    # Convert to dict
    data = search_response.model_dump()
    
    assert data["results"] == [1, 2, 3]
    assert data["token"] == "jwt_token_string"