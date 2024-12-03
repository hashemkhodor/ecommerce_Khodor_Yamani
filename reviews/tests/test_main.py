# test_main.py

from unittest.mock import MagicMock, patch

import pytest

# Import the FastAPI app
from app.main import app
from app.schemas import LoginRequest, PostReviewRequest, PutReviewRequest, Review
from fastapi.testclient import TestClient
from starlette import status

# Create a TestClient using the FastAPI app
client = TestClient(app)


# Fixture to mock the ReviewTable and its methods
@pytest.fixture
def mock_db():
    with patch("app.main.db") as mock_db:
        yield mock_db


# Fixture to mock the create_access_token function
@pytest.fixture
def mock_create_access_token():
    with patch("app.main.create_access_token") as mock_token:
        mock_token.return_value = "mock_token"
        yield mock_token


# Fixture to mock the decode_access_token function
@pytest.fixture
def mock_decode_access_token():
    with patch("app.main.decode_access_token") as mock_decode:
        yield mock_decode


def test_health_check_success():
    # Mock `get_purchases` to simulate successful database connection
    with patch(
        "app.main.db.customer_and_item_exist", return_value=[{"id": 1}, {"id": 2}]
    ):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "OK", "db_status": "connected"}


# Test cases for the /reviews/submit endpoint
def test_submit_review_success(mock_db):
    # Prepare test data
    review_request = {
        "customer_id": "customer1",
        "item_id": 1,
        "rating": 5,
        "comment": "Great product!",
    }
    # Mock the database methods
    mock_db.customer_and_item_exist.return_value = status.HTTP_200_OK
    mock_db.get_review.return_value = []
    mock_db.submit_review.return_value = [
        Review(**review_request, flagged="needs_approval")
    ]

    # Make the request
    response = client.post("/api/v1/reviews/submit", json=review_request)

    # Assert the response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Posted customer1's review for 1 successfully." in data["message"]


def test_submit_review_customer_or_item_missing(mock_db):
    review_request = {
        "customer_id": "customer1",
        "item_id": 1,
        "rating": 5,
        "comment": "Great product!",
    }
    # Mock the database methods to return bad request
    mock_db.customer_and_item_exist.return_value = status.HTTP_400_BAD_REQUEST

    response = client.post("/api/v1/reviews/submit", json=review_request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert (
        "Either customer 'customer1' or item with id '1' doesn't exist."
        in data["message"]
    )


def test_submit_review_already_exists(mock_db):
    review_request = {
        "customer_id": "customer1",
        "item_id": 1,
        "rating": 5,
        "comment": "Great product!",
    }
    # Mock the database methods
    mock_db.customer_and_item_exist.return_value = status.HTTP_200_OK
    mock_db.get_review.return_value = [Review(**review_request, flagged="approved")]

    response = client.post("/api/v1/reviews/submit", json=review_request)
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "customer1's review for 1 already exists." in data["message"]


def test_submit_review_db_error(mock_db):
    review_request = {
        "customer_id": "customer1",
        "item_id": 1,
        "rating": 5,
        "comment": "Great product!",
    }
    # Mock the database methods to raise an exception
    mock_db.customer_and_item_exist.side_effect = Exception("Database error")

    response = client.post("/api/v1/reviews/submit", json=review_request)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert "Internal Server Error." in data["message"]
    assert "Database error" in data.get("errors", "")


# Test cases for the /reviews/update endpoint
def test_update_review_success(mock_db):
    updated_review = {
        "customer_id": "customer1",
        "item_id": 1,
        "rating": 4,
        "comment": "Updated comment",
    }
    # Mock the database methods
    stored_review = Review(**updated_review, flagged="approved")
    mock_db.get_review.return_value = [stored_review]
    mock_db.update_review.return_value = [stored_review]

    response = client.put("/api/v1/reviews/update", json=updated_review)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        f"Updated {updated_review['customer_id']}'s review for {updated_review['item_id']} successfully."
        in data["message"]
    )


def test_update_review_not_found(mock_db):
    updated_review = {
        "customer_id": "customer1",
        "item_id": 1,
        "rating": 4,
        "comment": "Updated comment",
    }
    # Mock the database methods
    mock_db.get_review.return_value = []

    response = client.put("/api/v1/reviews/update", json=updated_review)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert (
        f"{updated_review['customer_id']}'s review for {updated_review['item_id']} not found"
        in data["message"]
    )


def test_update_review_db_error(mock_db):
    updated_review = {"customer_id": "customer1", "item_id": 1, "rating": 4}
    stored_review = Review(
        customer_id="customer1",
        item_id=1,
        rating=5,
        comment="Original comment",
        flagged="approved",
    )
    mock_db.get_review.return_value = [stored_review]
    mock_db.update_review.return_value = None  # Simulate DB error

    response = client.put("/api/v1/reviews/update", json=updated_review)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert "Internal Server Error." in data["message"]
    assert "Failed to update review" in data.get("errors", "")


# Test cases for the /reviews/delete endpoint
def test_delete_review_success(mock_db):
    mock_db.get_review.return_value = [
        Review(
            customer_id="customer1",
            item_id=1,
            rating=5,
            comment="Great product!",
            flagged="approved",
        )
    ]
    mock_db.delete_review.return_value = True

    response = client.delete(
        "/api/v1/reviews/delete", params={"customer_id": "customer1", "item_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Deleted review successfully." in data["message"]


def test_delete_review_not_found(mock_db):
    mock_db.get_review.return_value = []

    response = client.delete(
        "/api/v1/reviews/delete", params={"customer_id": "customer1", "item_id": 1}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "customer1's review for 1 not found" in data["message"]


def test_delete_review_db_error(mock_db):
    mock_db.get_review.return_value = [
        Review(
            customer_id="customer1",
            item_id=1,
            rating=5,
            comment="Great product!",
            flagged="approved",
        )
    ]
    mock_db.delete_review.side_effect = Exception("Database error")

    response = client.delete(
        "/api/v1/reviews/delete", params={"customer_id": "customer1", "item_id": 1}
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert "Internal Server Error." in data["message"]
    assert "Database error" in data.get("errors", "")


# Test cases for the /reviews/item/{item_id} endpoint
def test_get_item_review_success(mock_db):
    item_id = 1
    reviews = [
        Review(
            customer_id="customer1",
            item_id=item_id,
            rating=5,
            comment="Great product!",
            flagged="approved",
        ),
        Review(
            customer_id="customer2",
            item_id=item_id,
            rating=4,
            comment="Good product.",
            flagged="approved",
        ),
    ]
    mock_db.get_reviews.return_value = reviews

    response = client.get(f"/api/v1/reviews/item/{item_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Fetched reviews successfully for item_id 1." in data["message"]
    assert len(data["data"]) == 2


def test_get_item_review_no_reviews(mock_db):
    item_id = 1
    mock_db.get_reviews.return_value = []

    response = client.get(f"/api/v1/reviews/item/{item_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Fetched reviews successfully for item_id 1." in data["message"]
    assert len(data.get("data", [])) == 0


def test_get_item_review_db_error(mock_db):
    item_id = 1
    mock_db.get_reviews.return_value = None  # Simulate DB error

    response = client.get(f"/api/v1/reviews/item/{item_id}")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert "Internal Server Error." in data["message"]
    assert "Database Error" in data.get("errors", "")


# Test cases for the /reviews/customer/{customer_id} endpoint
def test_get_customer_review_success(mock_db):
    customer_id = "customer1"
    reviews = [
        Review(
            customer_id=customer_id,
            item_id=1,
            rating=5,
            comment="Great product!",
            flagged="approved",
        )
    ]
    mock_db.get_reviews.return_value = reviews

    response = client.get(f"/api/v1/reviews/customer/{customer_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        f"Fetched reviews successfully for customer_id {customer_id}."
        in data["message"]
    )
    assert len(data["data"]) == 1


# Test cases for the /reviews/details endpoint
def test_get_details_success(mock_db):
    params = {"customer_id": "customer1", "item_id": 1}
    reviews = [
        Review(
            customer_id=params["customer_id"],
            item_id=params["item_id"],
            rating=5,
            comment="Great product!",
            flagged="approved",
        )
    ]
    mock_db.get_reviews.return_value = reviews

    response = client.get("/api/v1/reviews/details", params=params)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        "Fetched reviews successfully for item_id 1 and customer_id customer1."
        in data["message"]
    )
    assert len(data["data"]) == 1


def test_get_details_missing_parameters():
    # Missing both item_id and customer_id
    response = client.get("/api/v1/reviews/details")
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    )  # FastAPI validation error


# Test cases for the /reviews/auth/login endpoint
def test_login_success(mock_db, mock_create_access_token):
    credentials = {"username": "admin", "password": "password123"}
    mock_db.client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {"username": "admin", "password": "password123", "role": "admin"}
    ]

    response = client.post("/api/v1/reviews/auth/login", json=credentials)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Successfully logged in" in data["message"]
    assert data["data"]["token"] == "mock_token"


def test_login_db_error(mock_db):
    credentials = {"username": "admin", "password": "password123"}
    mock_db.client.table.return_value.select.side_effect = Exception("Database error")

    response = client.post("/api/v1/reviews/auth/login", json=credentials)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert data["detail"] == "Database error"


# Test cases for the /reviews/moderate endpoint
def test_moderate_success(mock_db, mock_decode_access_token):
    # Mock admin user token
    mock_decode_access_token.return_value = {"username": "admin", "role": "admin"}
    # Mock database methods
    mock_db.customer_and_item_exist.return_value = status.HTTP_200_OK
    mock_db.get_review.return_value = [
        Review(
            customer_id="customer1",
            item_id=1,
            rating=5,
            comment="Great product!",
            flagged="needs_approval",
        )
    ]
    updated_review = Review(
        customer_id="customer1",
        item_id=1,
        rating=5,
        comment="Great product!",
        flagged="approved",
    )
    mock_db.update_review.return_value = [updated_review]

    params = {"customer_id": "customer1", "item_id": 1, "new_flag": "approved"}
    headers = {"Authorization": "Bearer valid_admin_token"}

    response = client.put("/api/v1/reviews/moderate", params=params, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        "Moderate review successfully for item_id 1 and customer_id customer1."
        in data["message"]
    )
    assert f"Changed it from" in data["message"]


def test_moderate_unauthorized(mock_db, mock_decode_access_token):
    # Mock customer user token
    mock_decode_access_token.return_value = {
        "username": "customer1",
        "role": "customer",
    }

    params = {"customer_id": "customer1", "item_id": 1, "new_flag": "approved"}
    headers = {"Authorization": "Bearer valid_customer_token"}

    response = client.put("/api/v1/reviews/moderate", params=params, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "User don't have the permission to perform this action" in data.get(
        "errors", ""
    )


def test_moderate_invalid_token(mock_db, mock_decode_access_token):
    # Mock invalid token
    mock_decode_access_token.return_value = "Invalid token"

    params = {"customer_id": "customer1", "item_id": 1, "new_flag": "approved"}
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.put("/api/v1/reviews/moderate", params=params, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "Invalid token" in data.get("errors", "")


def test_moderate_review_not_found(mock_db, mock_decode_access_token):
    # Mock admin user token
    mock_decode_access_token.return_value = {"username": "admin", "role": "admin"}
    # Mock database methods
    mock_db.customer_and_item_exist.return_value = status.HTTP_200_OK
    mock_db.get_review.return_value = []

    params = {"customer_id": "customer1", "item_id": 1, "new_flag": "approved"}
    headers = {"Authorization": "Bearer valid_admin_token"}

    response = client.put("/api/v1/reviews/moderate", params=params, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "customer1's review for 1 not found" in data["message"]


def test_moderate_db_error(mock_db, mock_decode_access_token):
    # Mock admin user token
    mock_decode_access_token.return_value = {"username": "admin", "role": "admin"}
    # Mock database methods
    mock_db.customer_and_item_exist.return_value = status.HTTP_200_OK
    mock_db.get_review.return_value = [
        Review(
            customer_id="customer1",
            item_id=1,
            rating=5,
            comment="Great product!",
            flagged="needs_approval",
        )
    ]
    mock_db.update_review.return_value = None  # Simulate DB error

    params = {"customer_id": "customer1", "item_id": 1, "new_flag": "approved"}
    headers = {"Authorization": "Bearer valid_admin_token"}

    response = client.put("/api/v1/reviews/moderate", params=params, headers=headers)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert "Internal Server Error." in data["message"]
    assert "Database Error" in data.get("errors", "")
