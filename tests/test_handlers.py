from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_statistics_handlers_with_empty_list(db_handlers) -> None:
    """Testing accessing '/api/statistics' via GET request."""
    response = client.get("/api/statistics")
    assert response.status_code == 200
    assert response.json() == {}


def test_save_statistics_handlers_object_not_exists(db_handlers) -> None:
    """Testing accessing '/api/statistics' via POST request."""
    response_json = {
        "date": "2000-01-01",
        "views": 100,
        "clicks": 200,
        "cost": 10.0
    }
    answer_json = {
        "statistics": {
            "date": response_json["date"],
            "views": response_json["views"],
            "clicks": response_json["clicks"],
            "cost": response_json["cost"],
        },
        "created": True,
        "aggregated": False,
    }
    response = client.post("/api/statistics", json=response_json)
    assert response.status_code == 201
    assert response.json() == answer_json


def test_reset_statistics_handler(db_handlers) -> None:
    """Testing accessing '/api/statistics' via DELETE request."""
    response = client.delete("/api/statistics")
    assert response.status_code == 200
    assert response.json() == {"message": "Deleted", "error": 0}
