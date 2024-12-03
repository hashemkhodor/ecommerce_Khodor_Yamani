# test_schemas.py

import pytest
from pydantic import ValidationError
from fastapi import status
import json
# Import the models and response classes from schemas.py
from app.schemas import (
    Review,
    LoginRequest,
    PostReviewRequest,
    PutReviewRequest,
    ModerateRequest,
    BaseCustomResponse,
    LoginResponse,
    PostReviewResponse,
    PutReviewResponse,
    DeleteReviewResponse,
    GetReviewsResponse,
    ModerateReviewsResponse,
)

# Test cases for the Review model
def test_review_model_valid():
    review_data = {
        "customer_id": "user123",
        "item_id": 456,
        "rating": 5,
        "comment": "Great product!",
        "flagged": "approved"
    }
    review = Review(**review_data)
    assert review.customer_id == "user123"
    assert review.item_id == 456
    assert review.rating == 5
    assert review.comment == "Great product!"
    assert review.flagged == "approved"
    assert review.time is None  # Default value

def test_review_model_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        Review()
    errors = exc_info.value.errors()
    expected_errors = [
        {'loc': ('customer_id',), 'msg': 'Field required', 'type': 'missing'},
        {'loc': ('item_id',), 'msg': 'Field required', 'type': 'missing'},
        {'loc': ('rating',), 'msg': 'Field required', 'type': 'missing'},
        {'loc': ('comment',), 'msg': 'Field required', 'type': 'missing'},
        {'loc': ('flagged',), 'msg': 'Field required', 'type': 'missing'},
    ]
    assert len(errors) == len(expected_errors)

def test_review_model_invalid_rating():
    with pytest.raises(ValidationError) as exc_info:
        Review(
            customer_id="user123",
            item_id=456,
            rating=6,  # Invalid rating (>5)
            comment="Great product!",
            flagged="approved"
        )
    errors = exc_info.value.errors()
    assert errors[0]['loc'] == ('rating',)
    assert 'less than or equal to 5' in errors[0]['msg']

def test_review_model_invalid_flagged_value():
    with pytest.raises(ValidationError) as exc_info:
        Review(
            customer_id="user123",
            item_id=456,
            rating=4,
            comment="Good product.",
            flagged="invalid_status"  # Invalid value
        )
    errors = exc_info.value.errors()
    assert errors[0]['loc'] == ('flagged',)
    assert "Input should be 'flagged', 'approved' or 'needs_approval'" in errors[0]['msg']

def test_review_model_optional_time():
    review_data = {
        "customer_id": "user123",
        "item_id": 456,
        "rating": 5,
        "comment": "Excellent!",
        "flagged": "approved",
        "time": "2023-10-01T12:00:00Z"
    }
    review = Review(**review_data)
    assert review.time == "2023-10-01T12:00:00Z"

def test_review_model_invalid_types():
    # Corrected test function with Strict types
    with pytest.raises(ValidationError) as exc_info:
        Review(
            customer_id=123,  # Should be str
            item_id="A456",    # Should be int
            rating="2A5",       # Should be int
            comment=789,      # Should be str
            flagged="approved"
        )
    errors = exc_info.value.errors()
    error_locs = [error['loc'] for error in errors]
    assert ('customer_id',) in error_locs
    assert ('item_id',) in error_locs
    assert ('rating',) in error_locs
    assert ('comment',) in error_locs
    assert len(errors) == 4

# Test cases for the LoginRequest model
def test_login_request_valid():
    login_data = {
        "username": "user123",
        "password": "securepassword"
    }
    login_request = LoginRequest(**login_data)
    assert login_request.username == "user123"
    assert login_request.password == "securepassword"

def test_login_request_missing_fields():
    with pytest.raises(ValidationError) as exc_info:
        LoginRequest()
    errors = exc_info.value.errors()
    expected_errors = [
        {'loc': ('username',), 'msg': 'Field required', 'type': 'missing'},
        {'loc': ('password',), 'msg': 'Field required', 'type': 'missing'},
    ]
    assert len(errors) == len(expected_errors)

# Test cases for the PostReviewRequest model
def test_post_review_request_valid():
    post_review_data = {
        "customer_id": "user123",
        "item_id": 456,
        "rating": 5,
        "comment": "Awesome product!"
    }
    post_review = PostReviewRequest(**post_review_data)
    assert post_review.customer_id == "user123"
    assert post_review.item_id == 456
    assert post_review.rating == 5
    assert post_review.comment == "Awesome product!"

def test_post_review_request_invalid_rating():
    with pytest.raises(ValidationError) as exc_info:
        PostReviewRequest(
            customer_id="user123",
            item_id=456,
            rating=-1,  # Invalid rating (<0)
            comment="Not good."
        )
    errors = exc_info.value.errors()
    assert errors[0]['loc'] == ('rating',)
    assert 'greater than or equal to 0' in errors[0]['msg']

# Test cases for the PutReviewRequest model
def test_put_review_request_valid():
    put_review_data = {
        "customer_id": "user123",
        "item_id": 456,
        "rating": 4,
        "comment": "Updated review."
    }
    put_review = PutReviewRequest(**put_review_data)
    assert put_review.customer_id == "user123"
    assert put_review.item_id == 456
    assert put_review.rating == 4
    assert put_review.comment == "Updated review."

def test_put_review_request_optional_fields():
    put_review_data = {
        "customer_id": "user123",
        "item_id": 456,

    }
    put_review = PutReviewRequest(**put_review_data)
    assert put_review.customer_id == "user123"
    assert put_review.item_id == 456
    assert put_review.rating is None
    assert put_review.comment is None

def test_put_review_request_invalid_rating():
    with pytest.raises(ValidationError) as exc_info:
        PutReviewRequest(
            customer_id="user123",
            item_id=456,
            rating=10  # Invalid rating (>5)
        )
    errors = exc_info.value.errors()
    assert errors[0]['loc'] == ('rating',)
    assert 'less than or equal to 5' in errors[0]['msg']

# Test cases for the ModerateRequest model
def test_moderate_request_valid():
    moderate_data = {
        "customer_id": "user123",
        "item_id": 456,
        "flag": "approved"
    }
    moderate_request = ModerateRequest(**moderate_data)
    assert moderate_request.customer_id == "user123"
    assert moderate_request.item_id == 456
    assert moderate_request.flag == "approved"

def test_moderate_request_invalid_flag():
    with pytest.raises(ValidationError) as exc_info:
        ModerateRequest(
            customer_id="user123",
            item_id=456,
            flag="invalid_flag"
        )
    errors = exc_info.value.errors()
    assert errors[0]['loc'] == ('flag',)
    assert "Input should be 'flagged', 'approved' or 'needs_approval'" in errors[0]['msg']

# Test cases for response classes
def test_login_response_success():
    credentials = LoginRequest(username="user123", password="securepassword")
    token = "mock_token"
    response = LoginResponse(status_code=200, credentials_schema=credentials, token=token)
    assert response.status_code == 200
    assert response.body
    content = response.body.decode('utf-8')
    assert f"User '{credentials.username}' logged in successfully." in content
    assert f'"token":"{token}"' in content

def test_login_response_invalid_credentials():
    credentials = LoginRequest(username="user123", password="wrongpassword")
    response = LoginResponse(status_code=401, credentials_schema=credentials)
    assert response.status_code == 401
    content = response.body.decode('utf-8')
    assert "Unauthorized. Incorrect username or password." in content

def test_post_review_response_success():
    review_request = PostReviewRequest(
        customer_id="user123",
        item_id=456,
        rating=5,
        comment="Great product!"
    )
    response = PostReviewResponse(status_code=200, review_schema=review_request)
    assert response.status_code == 200
    content = response.body.decode('utf-8')
    assert f"Posted {review_request.customer_id}'s review for {review_request.item_id} successfully." in content

def test_post_review_response_conflict():
    review_request = PostReviewRequest(
        customer_id="user123",
        item_id=456,
        rating=5,
        comment="Great product!"
    )
    response = PostReviewResponse(status_code=409, review_schema=review_request)
    assert response.status_code == 409
    content = response.body.decode('utf-8')
    assert f"{review_request.customer_id}'s review for {review_request.item_id} already exists." in content

def test_put_review_response_success():
    put_review_request = PutReviewRequest(
        customer_id="user123",
        item_id=456,
        rating=4,
        comment="Updated review."
    )
    response = PutReviewResponse(status_code=200, review_schema=put_review_request)
    assert response.status_code == 200
    content = response.body.decode('utf-8')
    assert f"Updated {put_review_request.customer_id}'s review for {put_review_request.item_id} successfully." in content
    assert '"rating":4' in content

def test_delete_review_response_success():
    response = DeleteReviewResponse(status_code=200, item_id=456, customer_id="user123")
    assert response.status_code == 200
    content = response.body.decode('utf-8')
    assert "Deleted review successfully." in content

def test_get_reviews_response_success():
    review1 = Review(
        customer_id="user123",
        item_id=456,
        rating=5,
        comment="Excellent!",
        flagged="approved"
    )
    review2 = Review(
        customer_id="user456",
        item_id=456,
        rating=4,
        comment="Very good!",
        flagged="approved"
    )
    response = GetReviewsResponse(
        status_code=200,
        item_id=456,
        reviews=[review1, review2]
    )
    assert response.status_code == 200
    content = response.body.decode('utf-8')
    assert "Fetched reviews successfully for item_id 456." in content
    assert '"customer_id":"user123"' in content
    assert '"customer_id":"user456"' in content

def test_moderate_reviews_response_success():
    review = Review(
        customer_id="user123",
        item_id=456,
        rating=5,
        comment="Great product!",
        flagged="needs_approval"
    )
    new_flag = "approved"
    response = ModerateReviewsResponse(
        status_code=200,
        item_id=456,
        customer_id="user123",
        new_flag=new_flag,
        review=review
    )
    assert response.status_code == 200
    content = response.body.decode('utf-8')
    assert f"Moderate review successfully for item_id {review.item_id} and customer_id {review.customer_id}." in content
    assert f"Changed it from {review.flagged} to {new_flag}" in content

def test_moderate_reviews_response_invalid_flag():
    with pytest.raises(AssertionError) as exc_info:
        ModerateReviewsResponse(
            status_code=200,
            item_id=456,
            customer_id="user123",
            new_flag="invalid_flag",
            review=None  # Missing review
        )
    assert "You must provide reviews if status code is good" in str(exc_info.value)

# Edge case tests
def test_review_model_rating_edge_cases():
    # Test rating at lower boundary
    review = Review(
        customer_id="user123",
        item_id=456,
        rating=0,
        comment="Not good.",
        flagged="flagged"
    )
    assert review.rating == 0

    # Test rating at upper boundary
    review = Review(
        customer_id="user123",
        item_id=456,
        rating=5,
        comment="Excellent!",
        flagged="approved"
    )
    assert review.rating == 5

def test_review_model_empty_comment():
    # Adjust according to whether empty comments are acceptable
    # Assuming empty comments are acceptable
    review = Review(
        customer_id="user123",
        item_id=456,
        rating=3,
        comment="",  # Empty comment
        flagged="needs_approval"
    )
    assert review.comment == ""

def test_review_model_missing_flagged():
    with pytest.raises(ValidationError) as exc_info:
        Review(
            customer_id="user123",
            item_id=456,
            rating=3,
            comment="Average product."
            # 'flagged' field missing
        )
    errors = exc_info.value.errors()
    assert errors[0]['loc'] == ('flagged',)
    assert errors[0]['msg'] == 'Field required'

def test_get_reviews_response_missing_reviews():
    with pytest.raises(AssertionError) as exc_info:
        GetReviewsResponse(
            status_code=200,
            item_id=456,
            reviews=None  # Missing reviews when status code is 200
        )
    assert "You must provide reviews if status code is good" in str(exc_info.value)

def test_get_reviews_response_invalid_status_code():
    with pytest.raises(ValueError) as exc_info:
        GetReviewsResponse(
            status_code=404,
            item_id=456,
            reviews=[]
        )
    assert "Unexpected status code: 404" in str(exc_info.value)
