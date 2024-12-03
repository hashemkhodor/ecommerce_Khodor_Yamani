#
#
# import pytest
# from datetime import timedelta
# from fastapi import HTTPException, status
#
# # Import your Customer model
# from app.schemas import Customer
#
# @pytest.fixture
# def setup_env(monkeypatch):
#     # Set environment variables
#     monkeypatch.setenv('JWT_SECRET_KEY', 'testsecretkey')
#     monkeypatch.setenv('JWT_ALOGRITHM', 'HS256')
#     # Re-import the module to ensure it picks up the environment variables
#     import sys
#     if 'app.utils' in sys.modules:
#         del sys.modules['app.utils']
#     global create_access_token, decode_access_token, get_current_user
#     yield
#     # Cleanup is handled by monkeypatch fixture
#
# def test_create_access_token(setup_env):
#     customer = Customer(
#         name="Test User",
#         username="testuser",
#         password="password123",
#         age=30,
#         address="123 Test St",
#         gender=True,
#         marital_status="single",
#         role="customer",
#     )
#     token = create_access_token(customer)
#     assert isinstance(token, str)
#     assert token
#
# def test_decode_access_token_valid(setup_env):
#     customer = Customer(
#         name="Test User",
#         username="testuser",
#         password="password123",
#         age=30,
#         address="123 Test St",
#         gender=True,
#         marital_status="single",
#         role="customer",
#     )
#     token = create_access_token(customer)
#     payload = decode_access_token(token)
#     assert isinstance(payload, dict)
#     assert payload['username'] == customer.username
#     assert payload['name'] == customer.name
#
#
#
# def test_decode_access_token_expired(setup_env):
#     customer = Customer(
#         name="Test User",
#         username="testuser",
#         password="password123",
#         age=30,
#         address="123 Test St",
#         gender=True,
#         marital_status="single",
#         role="customer",
#     )
#     # Create a token that expired 1 second ago
#     token = create_access_token(customer, expires_delta=timedelta(seconds=-1))
#     result = decode_access_token(token)
#     assert result == "Token has expired."
#
# def test_decode_access_token_invalid(setup_env):
#     invalid_token = "invalid.token.string"
#     result = decode_access_token(invalid_token)
#     assert result == "Invalid token."
#
# def test_get_current_user_valid(setup_env):
#     customer = Customer(
#         name="Test User",
#         username="testuser",
#         password="password123",
#         age=30,
#         address="123 Test St",
#         gender=True,
#         marital_status="single",
#         role="customer",
#     )
#     token = create_access_token(customer)
#     user = get_current_user(token)
#     assert user['username'] == customer.username
#     assert user['name'] == customer.name
#
# def test_get_current_user_expired(setup_env):
#     customer = Customer(
#         name="Expired User",
#         username="expireduser",
#         password="password123",
#         age=30,
#         address="123 Expired St",
#         gender=False,
#         marital_status="married",
#         role="customer",
#     )
#     # Token expired 1 second ago
#     token = create_access_token(customer, expires_delta=timedelta(seconds=-1))
#     with pytest.raises(HTTPException) as exc_info:
#         get_current_user(token)
#     assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
#     assert exc_info.value.detail == "Token has expired."
#     assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
#
# def test_get_current_user_invalid(setup_env):
#     invalid_token = "invalid.token.string"
#     with pytest.raises(HTTPException) as exc_info:
#         get_current_user(invalid_token)
#     assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
#     assert exc_info.value.detail == "Invalid token."
#     assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
