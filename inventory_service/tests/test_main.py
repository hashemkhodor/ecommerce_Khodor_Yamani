from unittest.mock import MagicMock, patch

import pytest
from app.main import app  # Assuming your FastAPI app is defined in main.py
from app.models import Good, GoodUpdate
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def good_data():
    return {
        "name": "Test Product",
        "category": "electronics",
        "price": 99.99,
        "description": "A test product",
        "count": 10,
    }


@pytest.fixture
def good_update_data():
    return {"price": 89.99, "count": 15}


def test_health_check_success():
    # Mock `get_purchases` to simulate successful database connection
    with patch("app.main.get_good", return_value=[{"id": 1}, {"id": 2}]):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "OK",
            "db_status": "connected",
            "sample_item_check": [{"id": 1}, {"id": 2}],
        }


def test_add_good_endpoint_success(good_data):
    with patch("app.main.add_good") as mock_add_good:
        mock_add_good.return_value = {"id": 1, **good_data}

        response = client.post("/api/v1/inventory/add", json=good_data)
        assert response.status_code == 200
        assert response.json() == {"id": 1, **good_data}
        mock_add_good.assert_called_once()


def test_add_good_endpoint_failure(good_data):
    with patch("app.main.add_good") as mock_add_good:
        mock_add_good.side_effect = Exception("Database error")

        response = client.post("/api/v1/inventory/add", json=good_data)
        assert response.status_code == 500
        assert response.json() == {"detail": "Database error"}
        mock_add_good.assert_called_once()


def test_update_good_endpoint_success(good_update_data):
    good_id = 1
    updated_good = {"id": good_id, **good_update_data}
    with patch("app.main.update_good") as mock_update_good:
        mock_update_good.return_value = updated_good

        response = client.put(
            f"/api/v1/inventory/update/{good_id}", json=good_update_data
        )
        assert response.status_code == 200
        assert response.json() == updated_good
        mock_update_good.assert_called_once_with(
            good_id, GoodUpdate(**good_update_data)
        )


def test_update_good_endpoint_not_found(good_update_data):
    good_id = 1
    with patch("app.main.update_good") as mock_update_good:
        mock_update_good.side_effect = ValueError("Item not found")

        response = client.put(
            f"/api/v1/inventory/update/{good_id}", json=good_update_data
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}
        mock_update_good.assert_called_once_with(
            good_id, GoodUpdate(**good_update_data)
        )


def test_get_good_endpoint_success(good_data):
    good_id = 1
    with patch("app.main.get_good") as mock_get_good:
        mock_get_good.return_value = {"id": good_id, **good_data}

        response = client.get(f"/api/v1/inventory/{good_id}")
        assert response.status_code == 200
        assert response.json() == {"id": good_id, **good_data}
        mock_get_good.assert_called_once_with(good_id)


def test_get_good_endpoint_not_found():
    good_id = 1
    with patch("app.main.get_good") as mock_get_good:
        mock_get_good.side_effect = ValueError("Item not found")

        response = client.get(f"/api/v1/inventory/{good_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}
        mock_get_good.assert_called_once_with(good_id)


def test_deduct_good_endpoint_success():
    good_id = 1
    with patch("app.main.deduct_good") as mock_deduct_good:
        mock_deduct_good.return_value = {
            "id": good_id,
            "message": "Deducted successfully",
        }

        response = client.put(f"/api/v1/inventory/deduct/{good_id}")
        assert response.status_code == 200
        assert response.json() == {"id": good_id, "message": "Deducted successfully"}
        mock_deduct_good.assert_called_once_with(good_id)


def test_deduct_good_endpoint_insufficient_stock():
    good_id = 1
    with patch("app.main.deduct_good") as mock_deduct_good:
        mock_deduct_good.side_effect = ValueError("Insufficient stock")

        response = client.put(f"/api/v1/inventory/deduct/{good_id}")
        assert response.status_code == 400
        assert response.json() == {"detail": "Insufficient stock"}
        mock_deduct_good.assert_called_once_with(good_id)
