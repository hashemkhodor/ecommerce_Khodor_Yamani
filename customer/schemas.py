from typing import Any, Literal, Optional, TypedDict, Union
from datetime import datetime

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, PositiveInt, field_validator

MaritalStatus = Literal["single", "married", "divorced", "widows"]
CustomerRole = Literal["customer", "moderator", "admin"]


class Customer(BaseModel):
    name: str
    username: str
    password: str
    age: int = Field(..., ge=0)
    address: str
    gender: bool
    marital_status: MaritalStatus
    role: CustomerRole


class Wallet(BaseModel):
    customer_id: str
    amount: float = Field(..., ge=0)
    last_updated: Optional[str] = None  # Automatically converted to datetime



class CustomerRegisterRequestSchema(BaseModel):
    name: str
    username: str
    password: str
    age: int = Field(..., ge=0)
    address: str
    gender: bool
    marital_status: MaritalStatus


class CustomerLoginSchema(BaseModel):
    username: str
    password: str


class CustomerUpdateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[PositiveInt] = None  # Optional positive integer
    address: Optional[str] = None
    gender: Optional[bool] = None
    marital_status: Optional[MaritalStatus] = None


class BaseCustomResponse(JSONResponse):
    """
    Base response class to handle shared logic for custom responses.
    """

    def __init__(
            self,
            status_code: int,
            message: str,
            data: Optional[Any] = None,
            notes: Optional[str] = None,
            errors: Optional[str] = None,
    ):
        content = {"message": message}
        if data is not None:
            content["data"] = data
        if notes:
            content["notes"] = notes
        if errors:
            content["errors"] = errors
        super().__init__(content=content, status_code=status_code)


class CustomerRegisterResponse(BaseCustomResponse):
    """
    Response for customer registration.
    """

    def __init__(
            self,
            status_code: int,
            register_schema: BaseModel,
            notes: Optional[str] = None,
            errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_201_CREATED:
            message = f"Registered '{register_schema.username}' successfully"

        elif status_code == status.HTTP_400_BAD_REQUEST:
            message = f"Failed to register {register_schema.username}"
        elif status_code == status.HTTP_409_CONFLICT:
            message = (
                f"Customer with username '{register_schema.username}' already exists"
            )
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try registering again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code, message=message, notes=notes, errors=errors
        )


class CustomerDeleteResponse(BaseCustomResponse):
    """
    Response for customer deletion.
    """

    def __init__(
            self,
            status_code: int,
            customer_id: str,
            notes: Optional[str] = None,
            errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_200_OK:
            message = f"Deleted '{customer_id}' successfully"
        elif status_code == status.HTTP_400_BAD_REQUEST:
            message = f"Failed to delete customer with id '{customer_id}'"
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"Customer with username '{customer_id}' not found"
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try deleting again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code, message=message, notes=notes, errors=errors
        )


class CustomerUpdateResponse(BaseCustomResponse):
    """
    Response for customer updates.
    """

    def __init__(
            self,
            status_code: int,
            customer_id: str,
            updated_customer: Optional[BaseModel] = None,
            notes: Optional[str] = None,
            errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_200_OK:
            if updated_customer is None:
                raise ValueError(
                    "Updated customer data must be provided for a 200 OK status"
                )
            message = f"Updated '{customer_id}' successfully"
            data = updated_customer.model_dump()
        elif status_code == status.HTTP_202_ACCEPTED:
            message = f"Customer update request for '{customer_id}' processed, but no new data available"
            data = None
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"Customer with username '{customer_id}' not found"
            data = None
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try updating again later"
            data = None
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            data=data,
            notes=notes,
            errors=errors,
        )


class CustomerGetResponse(BaseCustomResponse):
    """
    Response for retrieving customer information.
    """

    def __init__(
            self,
            status_code: int,
            customer_id: str,
            customer: Optional[BaseModel] = None,
            wallet: Optional[BaseModel] = None,
            notes: Optional[str] = None,
            errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_200_OK:
            if customer is None:
                raise ValueError("Customer data must be provided for a 200 OK status")
            message = f"Retrieved customer '{customer_id}' successfully"
            data = {"user": customer.model_dump(), "wallet": wallet.model_dump()}
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"Customer with username '{customer_id}' not found"
            data = None
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try retrieving again later"
            data = None
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            data=data,
            notes=notes,
            errors=errors,
        )


class WalletChargeResponse(BaseCustomResponse):
    """
    Response for wallet charge operation.
    """

    def __init__(
            self,
            status_code: int,
            customer_id: str,
            amount: float,
            new_balance: Optional[float] = None,
            notes: Optional[str] = None,
            errors: Optional[str] = None,
    ):
        data: Optional[dict[str, float]] = None

        if status_code == status.HTTP_200_OK:
            message = f"Wallet for customer '{customer_id}' charged with {amount}"
            data = {"new_balance": new_balance}

        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"Wallet for customer '{customer_id}' not found"
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try charging again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            data=data,
            notes=notes,
            errors=errors,
        )


class WalletDeductResponse(BaseCustomResponse):
    """
    Response for wallet deduction operation.
    """

    def __init__(
            self,
            status_code: int,
            customer_id: str,
            amount: float,
            new_balance: Optional[float] = None,
            notes: Optional[str] = None,
            errors: Optional[str] = None,
    ):
        data: Optional[dict[str, str | int | float]] = None
        if status_code == status.HTTP_200_OK:
            message = f"{amount} deducted from wallet for customer '{customer_id}'"
            data = {"new_balance": new_balance}
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"Wallet or customer '{customer_id}' not found"

        elif status_code == status.HTTP_400_BAD_REQUEST:
            message = "Insufficient funds in wallet"
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try deducting again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            data=data,
            notes=notes,
            errors=errors,
        )
