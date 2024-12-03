import json
from datetime import datetime

import pytest
from app.schemas import (
    Customer,
    CustomerDeleteResponse,
    CustomerGetResponse,
    CustomerLoginSchema,
    CustomerRegisterRequestSchema,
    CustomerRegisterResponse,
    CustomerUpdateResponse,
    CustomerUpdateSchema,
    Wallet,
    WalletChargeResponse,
    WalletDeductResponse,
)
from fastapi import status
from pydantic import ValidationError


# Test Customer Model
def test_customer_model_valid():
    customer = Customer(
        name="John Doe",
        username="johndoe",
        password="securepassword",
        age=30,
        address="123 Main St",
        gender=True,
        marital_status="single",
        role="customer",
    )
    assert customer.name == "John Doe"
    assert customer.age == 30


def test_customer_model_invalid_age():
    with pytest.raises(ValidationError):
        Customer(
            name="John Doe",
            username="johndoe",
            password="securepassword",
            age=-1,
            address="123 Main St",
            gender=True,
            marital_status="single",
            role="customer",
        )


# Test Wallet Model
def test_wallet_model_valid():
    wallet = Wallet(customer_id="123", amount=100.50, last_updated=str(datetime.now()))
    assert wallet.amount == 100.50


def test_wallet_model_invalid_amount():
    with pytest.raises(ValidationError):
        Wallet(customer_id="123", amount=-100.50)


# Test CustomerRegisterRequestSchema
def test_register_request_schema_valid():
    schema = CustomerRegisterRequestSchema(
        name="Jane Doe",
        username="janedoe",
        password="securepassword",
        age=25,
        address="456 Elm St",
        gender=False,
        marital_status="married",
    )
    assert schema.username == "janedoe"


def test_register_request_schema_invalid():
    with pytest.raises(ValidationError):
        CustomerRegisterRequestSchema(
            name="Jane Doe",
            username="janedoe",
            password="securepassword",
            age="invalid",  # Invalid type
            address="456 Elm St",
            gender=False,
            marital_status="married",
        )


# Test BaseCustomResponse and derived responses
def test_customer_register_response_created():
    response = CustomerRegisterResponse(
        status_code=status.HTTP_201_CREATED,
        register_schema=CustomerRegisterRequestSchema(
            name="Jane Doe",
            username="janedoe",
            password="securepassword",
            age=25,
            address="456 Elm St",
            gender=False,
            marital_status="married",
        ),
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.body.decode() == '{"message":"Registered \'janedoe\' successfully"}'


def test_customer_register_response_conflict():
    response = CustomerRegisterResponse(
        status_code=status.HTTP_409_CONFLICT,
        register_schema=CustomerRegisterRequestSchema(
            name="Jane Doe",
            username="janedoe",
            password="securepassword",
            age=25,
            address="456 Elm St",
            gender=False,
            marital_status="married",
        ),
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert (
        response.body.decode()
        == '{"message":"Customer with username \'janedoe\' already exists"}'
    )


def test_wallet_charge_response_success():
    response = WalletChargeResponse(
        status_code=status.HTTP_200_OK,
        customer_id="123",
        amount=50.0,
        new_balance=150.0,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.body.decode() == (
        '{"message":"Wallet for customer \'123\' charged with 50.0","data":{"new_balance":150.0}}'
    )


def test_wallet_charge_response_not_found():
    response = WalletChargeResponse(
        status_code=status.HTTP_404_NOT_FOUND, customer_id="123", amount=50.0
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        response.body.decode() == '{"message":"Wallet for customer \'123\' not found"}'
    )


def test_wallet_deduct_response_insufficient_funds():
    response = WalletDeductResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        customer_id="123",
        amount=100.0,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.body.decode() == '{"message":"Insufficient funds in wallet"}'


def test_customer_update_response_success():
    updated_customer = CustomerUpdateSchema(
        name="Updated Name",
        age=40,
        address="789 Pine St",
    )
    response = CustomerUpdateResponse(
        status_code=status.HTTP_200_OK,
        customer_id="123",
        updated_customer=updated_customer,
    )
    assert response.status_code == status.HTTP_200_OK

    # Parse the actual response body as JSON
    actual_body = json.loads(response.body.decode())

    # Define the expected dictionary
    expected_body = {
        "message": "Updated '123' successfully",
        "data": {
            "name": "Updated Name",
            "age": 40,
            "address": "789 Pine St",
            "gender": None,
            "marital_status": None,
        },
    }

    assert actual_body == expected_body
