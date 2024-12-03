import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Body, FastAPI
from fastapi.responses import JSONResponse
from loguru import logger

from app.models import CustomerTable
from app.schemas import (
    Customer,
    CustomerDeleteResponse,
    CustomerGetResponse,
    CustomerRegisterRequestSchema,
    CustomerRegisterResponse,
    CustomerUpdateResponse,
    CustomerUpdateSchema,
    Wallet,
    WalletChargeResponse,
    WalletDeductResponse,
)

load_dotenv()

db: CustomerTable = CustomerTable(
    url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY")
)


# Define router
router = APIRouter(prefix="/customer", tags=["Customer Management"])


@router.post("/auth/register")
async def register_customer(
    customer: CustomerRegisterRequestSchema,
) -> CustomerRegisterResponse:
    """
    Registers a new customer.

    Args:
        customer (CustomerRegisterRequestSchema): The customer registration details.

    Returns:
        CustomerRegisterResponse: Response object containing registration status and details.
    """
    try:

        if db.get_user(user_id=customer.username):
            return CustomerRegisterResponse(status_code=409, register_schema=customer)

        if db.create_customer(
            customer=Customer(**customer.model_dump(), role="customer")
        ):
            return CustomerRegisterResponse(status_code=201, register_schema=customer)

        return CustomerRegisterResponse(status_code=400, register_schema=customer)

    except Exception as e:
        logger.exception(e)
        return CustomerRegisterResponse(
            status_code=500, register_schema=customer, errors=str(e)
        )


@router.delete("/delete/{customer_id}")
async def delete_customer(customer_id: str):
    """
    Deletes a customer by their ID.

    Args:
        customer_id (str): The ID of the customer to delete.

    Returns:
        CustomerDeleteResponse: Response object containing deletion status.
    """
    try:
        if not db.get_user(user_id=customer_id):
            return CustomerDeleteResponse(status_code=404, customer_id=customer_id)

        if not db.delete_user(user_id=customer_id):
            return CustomerDeleteResponse(status_code=400, customer_id=customer_id)
        return CustomerDeleteResponse(status_code=200, customer_id=customer_id)

    except Exception as e:
        logger.exception(e)
        return CustomerDeleteResponse(
            status_code=500, customer_id=customer_id, errors=str(e)
        )


@router.put("/update/{customer_id}")
async def update_customer(customer_id: str, updates: CustomerUpdateSchema):
    """
    Updates a customer's information.

    Args:
        customer_id (str): The ID of the customer to update.
        updates (CustomerUpdateSchema): The updates to apply to the customer.

    Returns:
        CustomerUpdateResponse: Response object containing update status and updated data.
    """
    try:
        stored_customer: Optional[list[Customer]] = db.get_user(user_id=customer_id)
        if not db.get_user(user_id=customer_id):
            return CustomerUpdateResponse(status_code=404, customer_id=customer_id)

        stored_customer: Customer = stored_customer[0]

        updated_data = stored_customer.model_dump()
        if updates.model_dump(exclude_unset=True).items():
            for key, value in updates.model_dump(exclude_unset=True).items():
                updated_data[key] = value

        else:
            return CustomerUpdateResponse(status_code=202, customer_id=customer_id)

        updated_customer: Customer = Customer.model_validate(updated_data)

        status_code: int = (
            200
            if db.update_user(user_id=customer_id, new_customer=updated_customer)
            else 400
        )

        return CustomerUpdateResponse(
            status_code=status_code,
            customer_id=customer_id,
            updated_customer=updated_customer,
        )

    except Exception as e:
        logger.exception(e)
        return CustomerUpdateResponse(
            status_code=500, customer_id=customer_id, errors=str(e)
        )


@router.get("/get")
async def get_all_customers():
    """
    Retrieves all customers from the database.

    Returns:
        JSONResponse: JSON object containing all customers or an error message.
    """
    try:
        # data: list[dict] = list(
        #     map(lambda user: {user.username: user.model_dump()}, customers.values())
        # )
        data = list(
            map(lambda user: {user.username: user.model_dump()}, db.get_customers())
        )

        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        logger.exception(e)
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/get/{customer_id}")
async def get_customer(customer_id: str):
    """
    Retrieves a customer's details by their ID.

    Args:
        customer_id (str): The ID of the customer to retrieve.

    Returns:
        CustomerGetResponse: Response object containing customer details and wallet info.
    """
    try:
        customer: Optional[list[Customer]] = db.get_user(user_id=customer_id)
        if not customer:
            return CustomerGetResponse(status_code=404, customer_id=customer_id)
        # TODO - add wallet
        customer_wallet: Optional[list[Wallet]] = db.get_wallet(user_id=customer_id)
        if not customer_wallet:
            return CustomerGetResponse(status_code=404, customer_id=customer_id)

        return CustomerGetResponse(
            status_code=200,
            customer_id=customer_id,
            customer=customer[0],
            wallet=customer_wallet[0],
        )

    except Exception as e:
        logger.exception(e)
        return CustomerGetResponse(
            status_code=500, customer_id=customer_id, errors=str(e)
        )


@router.put("/wallet/{customer_id}/charge")
async def charge_wallet(customer_id: str, amount: float = Body(..., ge=0)):
    """
    Charges a customer's wallet by a specified amount.

    Args:
        customer_id (str): The ID of the customer whose wallet to charge.
        amount (float): The amount to add to the wallet. Must be non-negative.

    Returns:
        WalletChargeResponse: Response object containing new wallet balance or error.
    """
    try:
        customer_wallet: list[Wallet] = db.get_wallet(user_id=customer_id)
        if customer_wallet is None:
            return WalletChargeResponse(
                status_code=404, customer_id=customer_id, amount=amount
            )
        wallet: Optional[list[Wallet]] = db.charge_wallet(
            user_id=customer_id, amount=amount
        )

        if not wallet:
            return WalletChargeResponse(
                status_code=500,
                customer_id=customer_id,
                amount=-1,
                errors="DB not responding",
            )

        return WalletChargeResponse(
            status_code=200,
            customer_id=customer_id,
            amount=amount,
            new_balance=wallet[0].amount,
        )
    except Exception as e:
        logger.exception(e)
        return WalletChargeResponse(
            status_code=500, customer_id=customer_id, errors=str(e), amount=-1
        )


@router.put("/wallet/{customer_id}/deduct")
async def deduct_wallet(customer_id: str, amount: float = Body(..., ge=0)):
    """
    Deducts a specified amount from a customer's wallet.

    Args:
        customer_id (str): The ID of the customer whose wallet to deduct from.
        amount (float): The amount to deduct from the wallet. Must be non-negative.

    Returns:
        WalletDeductResponse: Response object containing new wallet balance or error.
    """
    try:
        customer_wallet: list[Wallet] = db.get_wallet(user_id=customer_id)
        if customer_wallet is None:
            return WalletDeductResponse(
                status_code=404, customer_id=customer_id, amount=amount
            )

        if customer_wallet[0].amount < amount:
            return WalletDeductResponse(
                status_code=400, customer_id=customer_id, amount=amount
            )

        wallet: Optional[list[Wallet]] = db.deduct_wallet(
            user_id=customer_id, amount=-amount
        )

        if not wallet:
            return WalletDeductResponse(
                status_code=500,
                customer_id=customer_id,
                amount=-1,
                errors="DB not responding",
            )

        return WalletDeductResponse(
            status_code=200,
            customer_id=customer_id,
            amount=amount,
            new_balance=wallet[0].amount,
        )
    except Exception as e:
        logger.exception(e)
        return WalletDeductResponse(
            status_code=500, customer_id=customer_id, errors=str(e), amount=-1
        )


app = FastAPI(
    title="Ecommerce Custom Router",
    description="Router for all customer related stuff",
    version="1.0.0",
    debug=True,
)
app.include_router(router, prefix="/api/v1")
