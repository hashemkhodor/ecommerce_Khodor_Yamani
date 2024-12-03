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

    Attributes:
        name (str): Full name of the customer.
        username (str): Unique username for the customer.
        password (str): Password for the customer account.
        age (int): Age of the customer (must be non-negative).
        address (str): Address of the customer.
        gender (bool): Gender of the customer (e.g., True for male, False for female).
        marital_status (MaritalStatus): Marital status of the customer.
        role (CustomerRole): Role of the customer (e.g., 'customer', 'moderator', 'admin').
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

    Attributes:
        customer_id (str): ID of the customer owning the wallet.
        amount (float): Wallet balance (must be non-negative).
        last_updated (Optional[str]): Timestamp of the last update to the wallet balance.
    """

    customer_id: str
    amount: float = Field(..., ge=0)
    last_updated: Optional[str] = None  # Automatically converted to datetime


class CustomerRegisterRequestSchema(BaseModel):
    """
    Schema for customer registration requests.

    Attributes:
        name (str): Full name of the customer.
        username (str): Unique username for the customer.
        password (str): Password for the customer account.
        age (int): Age of the customer (must be non-negative).
        address (str): Address of the customer.
        gender (bool): Gender of the customer.
        marital_status (MaritalStatus): Marital status of the customer.
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

    Attributes:
        username (str): The unique username of the customer.
        password (str): The password for the customer's account.
    """

    username: str
    password: str


class CustomerUpdateSchema(BaseModel):
    """
    Schema for updating customer information.

    Attributes:
        name (Optional[str]): The new full name of the customer.
        age (Optional[PositiveInt]): The new age of the customer. Must be a positive integer.
        address (Optional[str]): The new physical address of the customer.
        gender (Optional[bool]): The new gender of the customer. True for male, False for female.
        marital_status (Optional[MaritalStatus]): The new marital status of the customer.
    """

    name: Optional[str] = None
    age: Optional[PositiveInt] = None  # Optional positive integer
    address: Optional[str] = None
    gender: Optional[bool] = None
    marital_status: Optional[MaritalStatus] = None


class BaseCustomResponse(JSONResponse):
    """
    Base response class to handle shared logic for custom responses.

    Inherits from FastAPI's JSONResponse and standardizes the response structure.

    Attributes:
        status_code (int): The HTTP status code of the response.
        message (str): A descriptive message about the response.
        data (Optional[Any]): The payload of the response, if any.
        notes (Optional[str]): Additional notes regarding the response.
        errors (Optional[str]): Error details, if any.
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

        Args:
            status_code (int): The HTTP status code.
            message (str): A descriptive message.
            data (Optional[Any], optional): The response payload. Defaults to None.
            notes (Optional[str], optional): Additional notes. Defaults to None.
            errors (Optional[str], optional): Error details. Defaults to None.
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

    Inherits from BaseCustomResponse and customizes messages based on status codes.
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

        Args:
            status_code (int): The HTTP status code of the response.
            register_schema (BaseModel): The schema containing registration details.
            notes (Optional[str], optional): Additional notes. Defaults to None.
            errors (Optional[str], optional): Error details. Defaults to None.

        Raises:
            ValueError: If an unexpected status code is provided.
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

    Inherits from BaseCustomResponse and customizes messages based on status codes.
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

        Args:
            status_code (int): The HTTP status code of the response.
            customer_id (str): The ID of the customer being deleted.
            notes (Optional[str], optional): Additional notes. Defaults to None.
            errors (Optional[str], optional): Error details. Defaults to None.

        Raises:
            ValueError: If an unexpected status code is provided.
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

    Inherits from BaseCustomResponse and customizes messages based on status codes.
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

        Args:
            status_code (int): The HTTP status code of the response.
            customer_id (str): The ID of the customer being updated.
            updated_customer (Optional[BaseModel], optional): The updated customer data. Required if status is 200 OK.
            notes (Optional[str], optional): Additional notes. Defaults to None.
            errors (Optional[str], optional): Error details. Defaults to None.

        Raises:
            ValueError: If an unexpected status code is provided or if updated_customer is missing for 200 OK.
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

    Inherits from BaseCustomResponse and customizes messages based on status codes.
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

        Args:
            status_code (int): The HTTP status code of the response.
            customer_id (str): The ID of the customer being retrieved.
            customer (Optional[BaseModel], optional): The customer data. Required if status is 200 OK.
            wallet (Optional[BaseModel], optional): The wallet data. Required if status is 200 OK.
            notes (Optional[str], optional): Additional notes. Defaults to None.
            errors (Optional[str], optional): Error details. Defaults to None.

        Raises:
            ValueError: If an unexpected status code is provided or if customer data is missing for 200 OK.
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

    Inherits from BaseCustomResponse and customizes messages based on status codes.
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

        Args:
            status_code (int): The HTTP status code of the response.
            customer_id (str): The ID of the customer whose wallet is being charged.
            amount (float): The amount being added to the wallet.
            new_balance (Optional[float], optional): The new wallet balance after the charge.
                                                    Required if status is 200 OK.
            notes (Optional[str], optional): Additional notes. Defaults to None.
            errors (Optional[str], optional): Error details. Defaults to None.

        Raises:
            ValueError: If an unexpected status code is provided.
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

    Inherits from BaseCustomResponse and customizes messages based on status codes.
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

        Args:
            status_code (int): The HTTP status code of the response.
            customer_id (str): The ID of the customer whose wallet is being deducted.
            amount (float): The amount being deducted from the wallet.
            new_balance (Optional[float], optional): The new wallet balance after the deduction.
                                                    Required if status is 200 OK.
            notes (Optional[str], optional): Additional notes. Defaults to None.
            errors (Optional[str], optional): Error details. Defaults to None.

        Raises:
            ValueError: If an unexpected status code is provided.
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
