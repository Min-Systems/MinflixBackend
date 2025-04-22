from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "MinFlix API is running",
        "version": "6.0",
        "environment": "production",
        "endpoints": [
            "/login",
            "/registration",
            "/addprofile",
            "/editprofile",
            "/watchlater",
            "/favorite",
            "/watchhistory",
            "/getfilms",
            "/film",
            "/images"
        ]
    }