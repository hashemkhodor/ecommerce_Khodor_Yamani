from datetime import datetime
from typing import Any, Literal, Optional, TypedDict, Union

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, PositiveInt, field_validator

MaritalStatus = Literal["single", "married", "divorced", "widows"]
CustomerRole = Literal["customer", "moderator", "admin"]


class Customer(BaseModel):
    """
    Model representing a customer.

    :param name: Full name of the customer.
    :type name: str
    :param username: Unique username for the customer.
    :type username: str
    :param password: Password for the customer account.
    :type password: str
    :param age: Age of the customer (must be non-negative).
    :type age: int
    :param address: Address of the customer.
    :type address: str
    :param gender: Gender of the customer (e.g., True for male, False for female).
    :type gender: bool
    :param marital_status: Marital status of the customer.
    :type marital_status: MaritalStatus
    :param role: Role of the customer (e.g., 'customer', 'moderator', 'admin').
    :type role: CustomerRole
    """
    name: str
    username: str
    password: str
    age: int = Field(..., ge=0)
    address: str
    gender: bool
    marital_status: MaritalStatus
    role: CustomerRole


class Wallet(BaseModel):
    """
    Model representing a wallet.

    :param customer_id: ID of the customer owning the wallet.
    :type customer_id: str
    :param amount: Wallet balance (must be non-negative).
    :type amount: float
    :param last_updated: Timestamp of the last update to the wallet balance.
    :type last_updated: Optional[str]
    """

    customer_id: str
    amount: float = Field(..., ge=0)
    last_updated: Optional[str] = None  # Automatically converted to datetime


class CustomerRegisterRequestSchema(BaseModel):
    """
    Schema for customer registration requests.

    :param name: Full name of the customer.
    :type name: str
    :param username: Unique username for the customer.
    :type username: str
    :param password: Password for the customer account.
    :type password: str
    :param age: Age of the customer (must be non-negative).
    :type age: int
    :param address: Address of the customer.
    :type address: str
    :param gender: Gender of the customer.
    :type gender: bool
    :param marital_status: Marital status of the customer.
    :type marital_status: MaritalStatus
    """

    name: str
    username: str
    password: str
    age: int = Field(..., ge=0)
    address: str
    gender: bool
    marital_status: MaritalStatus


class CustomerLoginSchema(BaseModel):
    """
    Schema for customer login requests.

    :param username: The unique username of the customer.
    :type username: str
    :param password: The password for the customer's account.
    :type password: str
    """

    username: str
    password: str


class CustomerUpdateSchema(BaseModel):
    """
    Schema for updating customer information.

    :param name: The new full name of the customer.
    :type name: Optional[str]
    :param age: The new age of the customer. Must be a positive integer.
    :type age: Optional[PositiveInt]
    :param address: The new physical address of the customer.
    :type address: Optional[str]
    :param gender: The new gender of the customer. True for male, False for female.
    :type gender: Optional[bool]
    :param marital_status: The new marital status of the customer.
    :type marital_status: Optional[MaritalStatus]
    """

    name: Optional[str] = None
    age: Optional[PositiveInt] = None  # Optional positive integer
    address: Optional[str] = None
    gender: Optional[bool] = None
    marital_status: Optional[MaritalStatus] = None


class BaseCustomResponse(JSONResponse):
    """
    Base response class to handle shared logic for custom responses.

    :param status_code: The HTTP status code.
    :type status_code: int
    :param message: A descriptive message about the response.
    :type message: str
    :param data: The payload of the response, if any.
    :type data: Optional[Any]
    :param notes: Additional notes regarding the response.
    :type notes: Optional[str]
    :param errors: Error details, if any.
    :type errors: Optional[str]
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        data: Optional[Any] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the BaseCustomResponse.

        :param status_code: The HTTP status code.
        :type status_code: int
        :param message: A descriptive message.
        :type message: str
        :param data: The response payload. Defaults to None.
        :type data: Optional[Any]
        :param notes: Additional notes. Defaults to None.
        :type notes: Optional[str]
        :param errors: Error details. Defaults to None.
        :type errors: Optional[str]
        """

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
    Response for customer registration operations.

    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param register_schema: The schema containing registration details.
    :type register_schema: BaseModel
    :param notes: Additional notes.
    :type notes: Optional[str]
    :param errors: Error details.
    :type errors: Optional[str]
    """

    def __init__(
        self,
        status_code: int,
        register_schema: BaseModel,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the CustomerRegisterResponse.

        :raises ValueError: If an unexpected status code is provided.
        """

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
    Response for customer deletion operations.

    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param customer_id: The ID of the customer being deleted.
    :type customer_id: str
    :param notes: Additional notes.
    :type notes: Optional[str]
    :param errors: Error details.
    :type errors: Optional[str]
    """

    def __init__(
        self,
        status_code: int,
        customer_id: str,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the CustomerDeleteResponse.

        :raises ValueError: If an unexpected status code is provided.
        """

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
    Response for customer update operations.

    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param customer_id: The ID of the customer being updated.
    :type customer_id: str
    :param updated_customer: The updated customer data.
    :type updated_customer: Optional[BaseModel]
    :param notes: Additional notes.
    :type notes: Optional[str]
    :param errors: Error details.
    :type errors: Optional[str]
    """

    def __init__(
        self,
        status_code: int,
        customer_id: str,
        updated_customer: Optional[BaseModel] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the CustomerUpdateResponse.

        :raises ValueError: If an unexpected status code is provided or if updated_customer is missing for 200 OK.
        """

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

    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param customer_id: The ID of the customer being retrieved.
    :type customer_id: str
    :param customer: The customer data.
    :type customer: Optional[BaseModel]
    :param wallet: The wallet data.
    :type wallet: Optional[BaseModel]
    :param notes: Additional notes.
    :type notes: Optional[str]
    :param errors: Error details, if any.
    :type errors: Optional[str]
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
        """
        Initializes the CustomerGetResponse.

        :raises ValueError: If an unexpected status code is provided or if customer data is missing for 200 OK.
        """

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
    Response for wallet charge operations.

    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param customer_id: The ID of the customer whose wallet is being charged.
    :type customer_id: str
    :param amount: The amount being added to the wallet.
    :type amount: float
    :param new_balance: The new wallet balance after the charge.
    :type new_balance: Optional[float]
    :param notes: Additional notes, if any.
    :type notes: Optional[str]
    :param errors: Error details, if any.
    :type errors: Optional[str]
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
        """
        Initializes the WalletChargeResponse.

        :raises ValueError: If an unexpected status code is provided.
        """


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
    Response for wallet deduction operations.

    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param customer_id: The ID of the customer whose wallet is being deducted.
    :type customer_id: str
    :param amount: The amount being deducted from the wallet.
    :type amount: float
    :param new_balance: The new wallet balance after the deduction.
    :type new_balance: Optional[float]
    :param notes: Additional notes, if any.
    :type notes: Optional[str]
    :param errors: Error details, if any.
    :type errors: Optional[str]
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
        """
        Initializes the WalletDeductResponse.

        :raises ValueError: If an unexpected status code is provided.
        """

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
