# test_main.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.schemas import (
    CustomerRegisterRequestSchema,
    CustomerUpdateSchema,
    Customer,
    Wallet,
)
from app.models import CustomerTable

client = TestClient(app)


@patch("app.main.db")
def test_register_customer_success(mock_db):
    # Arrange
    customer_data = {
        "name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": True,
        "marital_status": "single",
    }

    # Mock the database methods
    mock_db.get_user.return_value = []  # User does not exist
    mock_db.create_customer.return_value = True  # Creation successful

    # Act
    response = client.post(
        "/api/v1/customer/auth/register",
        json=customer_data,
    )

    # Assert
    assert response.status_code == 201
    assert (
        response.json()["message"]
        == f"Registered '{customer_data['username']}' successfully"
    )
    mock_db.get_user.assert_called_once_with(user_id=customer_data["username"])
    mock_db.create_customer.assert_called_once()

    # Get the customer argument from keyword arguments
    called_args, called_kwargs = mock_db.create_customer.call_args
    created_customer = called_kwargs['customer']

    assert created_customer.username == customer_data["username"]
    assert created_customer.role == "customer"


@patch("app.main.db")
def test_register_customer_user_exists(mock_db):
    # Arrange
    customer_data = {
        "name": "Jane Doe",
        "username": "janedoe",
        "password": "password123",
        "age": 28,
        "address": "456 Main St",
        "gender": False,
        "marital_status": "married",
        "role": "customer",  # Add this line
    }

    # Mock the database methods
    mock_db.get_user.return_value = [Customer(**customer_data)]  # User exists

    # Act
    response = client.post(
        "/api/v1/customer/auth/register",
        json=customer_data,
    )

    # Assert
    assert response.status_code == 409
    assert (
        response.json()["message"]
        == f"Customer with username '{customer_data['username']}' already exists"
    )
    mock_db.get_user.assert_called_once_with(user_id=customer_data["username"])
    mock_db.create_customer.assert_not_called()


@patch("app.main.db")
def test_register_customer_failure(mock_db):
    # Arrange
    customer_data = {
        "name": "Bob Smith",
        "username": "bobsmith",
        "password": "password123",
        "age": 35,
        "address": "789 Main St",
        "gender": True,
        "marital_status": "divorced",
    }

    # Mock the database methods
    mock_db.get_user.return_value = []  # User does not exist
    mock_db.create_customer.return_value = False  # Creation failed

    # Act
    response = client.post(
        "/api/v1/customer/auth/register",
        json=customer_data,
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["message"] == f"Failed to register {customer_data['username']}"
    mock_db.get_user.assert_called_once_with(user_id=customer_data["username"])
    mock_db.create_customer.assert_called_once()


@patch("app.main.db")
def test_register_customer_exception(mock_db):
    # Arrange
    customer_data = {
        "name": "Error User",
        "username": "erroruser",
        "password": "password123",
        "age": 40,
        "address": "101 Error St",
        "gender": True,
        "marital_status": "single",
    }

    # Mock the database methods to raise an exception
    mock_db.get_user.side_effect = Exception("Database Error")

    # Act
    response = client.post(
        "/api/v1/customer/auth/register",
        json=customer_data,
    )

    # Assert
    assert response.status_code == 500
    assert (
        response.json()["message"]
        == "Internal Server Error. Please try registering again later"
    )
    mock_db.get_user.assert_called_once_with(user_id=customer_data["username"])
    mock_db.create_customer.assert_not_called()


@patch("app.main.db")
def test_delete_customer_success(mock_db):
    # Arrange
    customer_id = "johndoe"

    # Mock the database methods
    stored_customer = Customer(
        name="John Doe",
        username=customer_id,
        password="password123",
        age=30,
        address="123 Main St",
        gender=True,
        marital_status="single",
        role="customer",
    )
    mock_db.get_user.return_value = [stored_customer]
    mock_db.delete_user.return_value = True

    # Act
    response = client.delete(f"/api/v1/customer/delete/{customer_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Deleted '{customer_id}' successfully"
    mock_db.get_user.assert_called_once_with(user_id=customer_id)
    mock_db.delete_user.assert_called_once_with(user_id=customer_id)


@patch("app.main.db")
def test_delete_customer_not_found(mock_db):
    # Arrange
    customer_id = "nonexistentuser"

    # Mock the database methods
    mock_db.get_user.return_value = []

    # Act
    response = client.delete(f"/api/v1/customer/delete/{customer_id}")

    # Assert
    assert response.status_code == 404
    assert (
        response.json()["message"]
        == f"Customer with username '{customer_id}' not found"
    )
    mock_db.get_user.assert_called_once_with(user_id=customer_id)
    mock_db.delete_user.assert_not_called()


@patch("app.main.db")
def test_delete_customer_failure(mock_db):
    # Arrange
    customer_id = "johndoe"

    # Mock the database methods
    stored_customer = Customer(
        name="John Doe",
        username=customer_id,
        password="password123",
        age=30,
        address="123 Main St",
        gender=True,
        marital_status="single",
        role="customer",
    )
    mock_db.get_user.return_value = [stored_customer]
    mock_db.delete_user.return_value = False

    # Act
    response = client.delete(f"/api/v1/customer/delete/{customer_id}")

    # Assert
    assert response.status_code == 400
    assert (
        response.json()["message"]
        == f"Failed to delete customer with id '{customer_id}'"
    )
    mock_db.get_user.assert_called_once_with(user_id=customer_id)
    mock_db.delete_user.assert_called_once_with(user_id=customer_id)


@patch("app.main.db")
def test_delete_customer_exception(mock_db):
    # Arrange
    customer_id = "erroruser"

    # Mock the database methods to raise an exception
    mock_db.get_user.side_effect = Exception("Database Error")

    # Act
    response = client.delete(f"/api/v1/customer/delete/{customer_id}")

    # Assert
    assert response.status_code == 500
    assert (
        response.json()["message"]
        == "Internal Server Error. Please try deleting again later"
    )
    mock_db.get_user.assert_called_once_with(user_id=customer_id)
    mock_db.delete_user.assert_not_called()


@patch("app.main.db")
def test_update_customer_success(mock_db):
    # Arrange
    customer_id = "johndoe"
    updates = {
        "name": "John Updated",
        "age": 31,
    }

    stored_customer = Customer(
        name="John Doe",
        username=customer_id,
        password="password123",
        age=30,
        address="123 Main St",
        gender=True,
        marital_status="single",
        role="customer",
    )

    updated_customer = Customer(
        name="John Updated",
        username=customer_id,
        password="password123",
        age=31,
        address="123 Main St",
        gender=True,
        marital_status="single",
        role="customer",
    )

    # Mock the database methods
    mock_db.get_user.return_value = [stored_customer]
    mock_db.update_user.return_value = [updated_customer]

    # Act
    response = client.put(
        f"/api/v1/customer/update/{customer_id}",
        json=updates,
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Updated '{customer_id}' successfully"
    assert response.json()["data"] == updated_customer.model_dump()
    mock_db.get_user.assert_called_with(user_id=customer_id)
    mock_db.update_user.assert_called_once()


@patch("app.main.db")
def test_update_customer_no_changes(mock_db):
    # Arrange
    customer_id = "johndoe"
    updates = {}  # No updates provided

    stored_customer = Customer(
        name="John Doe",
        username=customer_id,
        password="password123",
        age=30,
        address="123 Main St",
        gender=True,
        marital_status="single",
        role="customer",
    )

    # Mock the database methods
    mock_db.get_user.return_value = [stored_customer]

    # Act
    response = client.put(
        f"/api/v1/customer/update/{customer_id}",
        json=updates,
    )

    # Assert
    assert response.status_code == 202
    assert (
        response.json()["message"]
        == f"Customer update request for '{customer_id}' processed, but no new data available"
    )
    mock_db.get_user.assert_called_with(user_id=customer_id)
    mock_db.update_user.assert_not_called()


@patch("app.main.db")
def test_update_customer_not_found(mock_db):
    # Arrange
    customer_id = "nonexistentuser"
    updates = {
        "name": "Nonexistent User",
    }

    # Mock the database methods
    mock_db.get_user.return_value = []

    # Act
    response = client.put(
        f"/api/v1/customer/update/{customer_id}",
        json=updates,
    )

    # Assert
    assert response.status_code == 404
    assert (
        response.json()["message"]
        == f"Customer with username '{customer_id}' not found"
    )
    mock_db.get_user.assert_called_with(user_id=customer_id)
    mock_db.update_user.assert_not_called()


@patch("app.main.db")
def test_get_all_customers_success(mock_db):
    # Arrange
    customers = [
        Customer(
            name="John Doe",
            username="johndoe",
            password="password123",
            age=30,
            address="123 Main St",
            gender=True,
            marital_status="single",
            role="customer",
        ),
        Customer(
            name="Jane Doe",
            username="janedoe",
            password="password123",
            age=28,
            address="456 Main St",
            gender=False,
            marital_status="married",
            role="customer",
        ),
    ]

    # Mock the database methods
    mock_db.get_customers.return_value = customers

    # Act
    response = client.get("/api/v1/customer/get")

    # Assert
    assert response.status_code == 200
    expected_data = [
        {customer.username: customer.model_dump()} for customer in customers
    ]
    assert response.json()["data"] == expected_data
    mock_db.get_customers.assert_called_once()


@patch("app.main.db")
def test_get_all_customers_exception(mock_db):
    # Arrange
    # Mock the database methods to raise an exception
    mock_db.get_customers.side_effect = Exception("Database Error")

    # Act
    response = client.get("/api/v1/customer/get")

    # Assert
    assert response.status_code == 500
    assert "error" in response.json()
    mock_db.get_customers.assert_called_once()


@patch("app.main.db")
def test_get_customer_success(mock_db):
    # Arrange
    customer_id = "johndoe"
    customer = Customer(
        name="John Doe",
        username=customer_id,
        password="password123",
        age=30,
        address="123 Main St",
        gender=True,
        marital_status="single",
        role="customer",
    )
    wallet = Wallet(
        customer_id=customer_id,
        amount=100.0,
        last_updated=None,
    )

    # Mock the database methods
    mock_db.get_user.return_value = [customer]
    mock_db.get_wallet.return_value = [wallet]

    # Act
    response = client.get(f"/api/v1/customer/get/{customer_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Retrieved customer '{customer_id}' successfully"
    assert response.json()["data"] == {
        "user": customer.model_dump(),
        "wallet": wallet.model_dump(),
    }
    mock_db.get_user.assert_called_once_with(user_id=customer_id)
    mock_db.get_wallet.assert_called_once_with(user_id=customer_id)


@patch("app.main.db")
def test_get_customer_not_found(mock_db):
    # Arrange
    customer_id = "nonexistentuser"

    # Mock the database methods
    mock_db.get_user.return_value = []
    mock_db.get_wallet.return_value = None

    # Act
    response = client.get(f"/api/v1/customer/get/{customer_id}")

    # Assert
    assert response.status_code == 404
    assert (
        response.json()["message"]
        == f"Customer with username '{customer_id}' not found"
    )
    mock_db.get_user.assert_called_once_with(user_id=customer_id)
    mock_db.get_wallet.assert_not_called()


@patch("app.main.db")
def test_charge_wallet_success(mock_db):
    # Arrange
    customer_id = "johndoe"
    amount = 50.0
    wallet_before = Wallet(
        customer_id=customer_id,
        amount=100.0,
        last_updated=None,
    )
    wallet_after = Wallet(
        customer_id=customer_id,
        amount=150.0,
        last_updated=None,
    )

    # Mock the database methods
    mock_db.get_wallet.return_value = [wallet_before]
    mock_db.charge_wallet.return_value = [wallet_after]

    # Act
    response = client.put(
        f"/api/v1/customer/wallet/{customer_id}/charge",
        json=amount,
    )

    # Assert
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == f"Wallet for customer '{customer_id}' charged with {amount}"
    )
    assert response.json()["data"]["new_balance"] == wallet_after.amount
    mock_db.get_wallet.assert_called_once_with(user_id=customer_id)
    mock_db.charge_wallet.assert_called_once_with(user_id=customer_id, amount=amount)


@patch("app.main.db")
def test_charge_wallet_not_found(mock_db):
    # Arrange
    customer_id = "nonexistentuser"
    amount = 50.0

    # Mock the database methods
    mock_db.get_wallet.return_value = None

    # Act
    response = client.put(
        f"/api/v1/customer/wallet/{customer_id}/charge",
        json=amount,
    )

    # Assert
    assert response.status_code == 404
    assert (
        response.json()["message"]
        == f"Wallet for customer '{customer_id}' not found"
    )
    mock_db.get_wallet.assert_called_once_with(user_id=customer_id)
    mock_db.charge_wallet.assert_not_called()


@patch("app.main.db")
def test_deduct_wallet_success(mock_db):
    # Arrange
    customer_id = "johndoe"
    amount = 50.0
    wallet_before = Wallet(
        customer_id=customer_id,
        amount=100.0,
        last_updated=None,
    )
    wallet_after = Wallet(
        customer_id=customer_id,
        amount=50.0,
        last_updated=None,
    )

    # Mock the database methods
    mock_db.get_wallet.return_value = [wallet_before]
    mock_db.deduct_wallet.return_value = [wallet_after]

    # Act
    response = client.put(
        f"/api/v1/customer/wallet/{customer_id}/deduct",
        json=amount,
    )

    # Assert
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == f"{amount} deducted from wallet for customer '{customer_id}'"
    )
    assert response.json()["data"]["new_balance"] == wallet_after.amount
    mock_db.get_wallet.assert_called_once_with(user_id=customer_id)
    mock_db.deduct_wallet.assert_called_once_with(user_id=customer_id, amount=-amount)


@patch("app.main.db")
def test_deduct_wallet_insufficient_funds(mock_db):
    # Arrange
    customer_id = "johndoe"
    amount = 150.0
    wallet_before = Wallet(
        customer_id=customer_id,
        amount=100.0,
        last_updated=None,
    )

    # Mock the database methods
    mock_db.get_wallet.return_value = [wallet_before]

    # Act
    response = client.put(
        f"/api/v1/customer/wallet/{customer_id}/deduct",
        json=amount,
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["message"] == "Insufficient funds in wallet"
    mock_db.get_wallet.assert_called_once_with(user_id=customer_id)
    mock_db.deduct_wallet.assert_not_called()
