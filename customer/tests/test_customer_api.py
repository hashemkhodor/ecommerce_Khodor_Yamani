import pytest
from fastapi import status
from httpx import AsyncClient

from customer.router import app  # Adjust the import path as needed for your app


@pytest.fixture
def test_client():
    """Fixture for AsyncClient"""
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.mark.asyncio
async def test_register_customer(test_client):
    customer_data = {
        "name": "John Doe",
        "username": "johndoe",
        "password": "securepassword123",
        "age": 30,
        "address": "123 Main St",
        "gender": True,
        "marital_status": "single",
    }
    response = await test_client.post(
        "/api/v1/customer/auth/register", json=customer_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert (
        response.json()["message"]
        == f"Registered {customer_data['username']} successfully"
    )

    # Duplicate username should result in a conflict
    response = await test_client.post(
        "/api/v1/customer/auth/register", json=customer_data
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        f"Customer with username \"{customer_data['username']}\" already exists"
        in response.json()["message"]
    )


@pytest.mark.asyncio
async def test_delete_customer(test_client):
    # Create a customer for deletion
    customer_data = {
        "name": "Jane Doe",
        "username": "janedoe",
        "password": "password123",
        "age": 25,
        "address": "456 Elm St",
        "gender": False,
        "marital_status": "married",
    }
    await test_client.post("/api/v1/customer/auth/register", json=customer_data)

    # Delete the customer
    response = await test_client.delete(
        f"/api/v1/customer/delete/{customer_data['username']}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == f"Deleted '{customer_data['username']}' successfully"
    )

    # Try to delete a non-existent customer
    response = await test_client.delete(
        f"/api/v1/customer/delete/{customer_data['username']}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        f"Customer with username '{customer_data['username']}' not found"
        in response.json()["message"]
    )


@pytest.mark.asyncio
async def test_update_customer(test_client):
    # Register a customer to update
    customer_data = {
        "name": "Jake Smith",
        "username": "jakesmith",
        "password": "pass123",
        "age": 35,
        "address": "789 Pine St",
        "gender": True,
        "marital_status": "divorced",
    }
    await test_client.post("/api/v1/customer/auth/register", json=customer_data)

    # Update the customer's data
    update_data = {"age": 36, "address": "Updated Address"}
    response = await test_client.put(
        f"/api/v1/customer/update/{customer_data['username']}", json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == f"Updated '{customer_data['username']}' successfully"
    )
    assert response.json()["data"]["age"] == 36
    assert response.json()["data"]["address"] == "Updated Address"
    # TODO - assert all other fields are unchanged

    # Try to update a non-existent customer
    response = await test_client.put(
        "/api/v1/customer/update/nonexistentuser", json=update_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        "Customer with username 'nonexistentuser' not found"
        in response.json()["message"]
    )

    # TODO - Try to update a customer but without specifying any field. (Empty body)


@pytest.mark.asyncio
async def test_wallet_operations(test_client):
    # Register a customer with a wallet
    customer_data = {
        "name": "Emily Clark",
        "username": "emilyclark",
        "password": "pass456",
        "age": 28,
        "address": "321 Maple St",
        "gender": False,
        "marital_status": "single",
    }
    await test_client.post("/api/v1/customer/auth/register", json=customer_data)

    # Charge the wallet
    charge_amount = 100.0
    response = await test_client.put(
        f"/api/v1/customer/wallet/{customer_data['username']}/charge",
        json=charge_amount,
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == f"Wallet for customer '{customer_data['username']}' charged with {charge_amount}"
    )
    assert response.json()["data"]["new_balance"] == charge_amount

    # Deduct from the wallet
    deduct_amount = 50.0
    response = await test_client.put(
        f"/api/v1/customer/wallet/{customer_data['username']}/deduct",
        json=deduct_amount,
    )
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == f"{deduct_amount} deducted from wallet for customer '{customer_data['username']}'"
    )
    assert response.json()["data"]["new_balance"] == charge_amount - deduct_amount

    # Deduct more than available funds
    overdraft_amount = 100.0
    response = await test_client.put(
        f"/api/v1/customer/wallet/{customer_data['username']}/deduct",
        json=overdraft_amount,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Insufficient funds in wallet" in response.json()["message"]

    # Try wallet operation on non-existent customer
    response = await test_client.put(
        "/api/v1/customer/wallet/nonexistentuser/charge", json=charge_amount
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        f"Wallet for customer 'nonexistentuser' not found" in response.json()["message"]
    )
