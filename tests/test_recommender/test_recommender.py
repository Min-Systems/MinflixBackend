import pytest
import numpy as np
from app.recommender.recommender import recommend, cosine_similarity, films

def test_cosine_similarity_identical_vectors():
    """Test cosine similarity between identical vectors."""
    vec_a = np.array([1, 0, 1, 0])
    vec_b = np.array([1, 0, 1, 0])
    
    result = cosine_similarity(vec_a, vec_b)
    
    # Use numpy's isclose instead of exact equality
    assert np.isclose(result, 1.0)
    # Or use pytest's approx
    assert result == pytest.approx(1.0)

def test_cosine_similarity_orthogonal_vectors():
    """Test cosine similarity between orthogonal vectors."""
    vec_a = np.array([1, 0, 0, 0])
    vec_b = np.array([0, 1, 0, 0])
    
    result = cosine_similarity(vec_a, vec_b)
    
    # Use a tolerance for comparing with zero
    assert np.isclose(result, 0.0)
    # Or
    assert result == pytest.approx(0.0)

def test_cosine_similarity_opposite_vectors():
    """Test cosine similarity between opposite vectors."""
    vec_a = np.array([1, 0, 0, 0])
    vec_b = np.array([-1, 0, 0, 0])
    
    result = cosine_similarity(vec_a, vec_b)
    
    assert np.isclose(result, -1.0)
    # Or
    assert result == pytest.approx(-1.0)
