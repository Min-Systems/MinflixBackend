from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "MinFlix API is running",
        "version": "8.0",
        "environment": "production",
        "endpoints": [
            "/login",
            "/registration",
            "/addprofile",
            "/editprofile",
            "/watchlater",
            "/favorite",
            "/watchhistory",
            "/search",
            "/getfilms",
            "/film",
            "/images",
            "/recommendations",
        ]
    }
