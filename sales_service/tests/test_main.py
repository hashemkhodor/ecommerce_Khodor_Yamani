from unittest.mock import patch

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# Test for the health check endpoint
def test_health_check_success():
    # Mock `get_purchases` to simulate successful database connection
    with patch("app.main.get_purchases", return_value=[{"id": 1}, {"id": 2}]):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "OK",
            "db_status": "connected",
            "records_found": 2,
        }


def test_health_check_failure():
    # Mock `get_purchases` to simulate a database error
    with patch("app.main.get_purchases", side_effect=Exception("Database error")):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ERROR"
        assert response.json()["db_status"] == "disconnected"
        assert "error" in response.json()


# Test for fetching all purchases
def test_fetch_all_purchases_success():
    # Mock `get_purchases` to return a list of purchases
    mock_purchases = [{"id": 1, "amount": 100.0}, {"id": 2, "amount": 50.0}]
    with patch("app.main.get_purchases", return_value=mock_purchases):
        response = client.get("/api/v1/sales/get")
        assert response.status_code == 200
        assert response.json() == mock_purchases


def test_fetch_all_purchases_failure():
    with patch("app.main.get_purchases", side_effect=Exception("Database error")):
        response = client.get("/api/v1/sales/get")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}


# Test for purchasing a good
def test_purchase_good_success():
    # Mock `process_purchase` to simulate a successful purchase
    mock_response = {"message": "Purchase successful"}
    with patch("app.main.process_purchase", return_value=mock_response):
        response = client.post("/api/v1/sales/purchase/testuser/123")
        assert response.status_code == 200
        assert response.json() == mock_response


def test_purchase_good_value_error():
    # Mock `process_purchase` to raise a ValueError
    with patch("app.main.process_purchase", side_effect=ValueError("Invalid purchase")):
        response = client.post("/api/v1/sales/purchase/testuser/123")
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid purchase"


def test_purchase_good_general_error():
    # Mock `process_purchase` to raise a generic exception
    with patch("app.main.process_purchase", side_effect=Exception("Unexpected error")):
        response = client.post("/api/v1/sales/purchase/testuser/123")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
