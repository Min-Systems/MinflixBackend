from app.recommender.recommender import * 
import numpy as np

def test_cosine_similarity():
    """Test the cosine similarity function."""
    vec_a = np.array([1, 0, 1, 0])
    vec_b = np.array([1, 0, 1, 0])
    similarity = cosine_similarity(vec_a, vec_b)
    assert similarity == 1.0  # Same vectors should have similarity of 1

def test_recommend():
    """Test the recommendation function returns the expected number of results."""
    results = recommend("Evil Brain From Outer Space")
    assert len(results) == 2  # Should return top_n=2 results
    assert "Evil Brain From Outer Space" not in results  # Shouldn't include the input film