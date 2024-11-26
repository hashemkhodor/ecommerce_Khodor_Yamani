from typing import Dict

from fastapi import APIRouter, Body, FastAPI
from fastapi.responses import JSONResponse

from customer.schemas import (
    Customer,
    Wallet,
    CustomerRegisterRequestSchema,
    CustomerRegisterResponse,
    CustomerDeleteResponse,
    CustomerUpdateSchema,
    CustomerUpdateResponse,
    CustomerGetResponse,
    WalletChargeResponse,
    WalletDeductResponse,
)

# from models import Customer, Wallet

customers: Dict[str, Customer] = {}
wallets: Dict[str, Wallet] = {}

# Define router
router = APIRouter(prefix="/customer", tags=["Customer Management"])


@router.post("/auth/register")
async def register_customer(
    customer: CustomerRegisterRequestSchema,
) -> CustomerRegisterResponse:
    try:
        if customer.username in customers:
            return CustomerRegisterResponse(status_code=409, register_schema=customer)

        customers[customer.username] = Customer(
            **customer.model_dump(), role="customer"
        )
        wallets[customer.username] = Wallet(customer_id=customer.username, amount=0.0)
        return CustomerRegisterResponse(status_code=201, register_schema=customer)

    except Exception as e:
        return CustomerRegisterResponse(
            status_code=500, register_schema=customer, errors=str(e)
        )


@router.delete("/delete/{customer_id}")
async def delete_customer(customer_id: str):
    try:
        if customer_id not in customers:
            return CustomerDeleteResponse(status_code=404, customer_id=customer_id)

        del customers[customer_id]
        if customer_id in wallets:
            del wallets[customer_id]
        return CustomerDeleteResponse(status_code=200, customer_id=customer_id)

    except Exception as e:
        return CustomerDeleteResponse(
            status_code=500, customer_id=customer_id, errors=str(e)
        )


@router.put("/update/{customer_id}")
async def update_customer(customer_id: str, updates: CustomerUpdateSchema):
    try:
        if customer_id not in customers:
            return CustomerUpdateResponse(status_code=404, customer_id=customer_id)

        stored_customer = customers[customer_id]
        updated_data = stored_customer.model_dump()
        if updates.model_dump(exclude_unset=True).items():
            for key, value in updates.model_dump(exclude_unset=True).items():
                updated_data[key] = value
        else:
            return CustomerUpdateResponse(status_code=202, customer_id=customer_id)

        customers[customer_id] = Customer(**updated_data)
        return CustomerUpdateResponse(
            status_code=200,
            customer_id=customer_id,
            updated_customer=customers[customer_id],
        )

    except Exception as e:
        return CustomerUpdateResponse(status_code=500, errors=str(e))


@router.get("/get")
async def get_all_customers():
    try:
        data: list[dict] = list(
            map(lambda user: {user.username: user.model_dump()}, customers.values())
        )
        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/get/{customer_id}")
async def get_customer(customer_id: str):
    try:
        if customer_id not in customers:
            return CustomerGetResponse(status_code=404, customer_id=customer_id)
        return CustomerGetResponse(
            status_code=200, customer_id=customer_id, customer=customers[customer_id]
        )

    except Exception as e:
        return CustomerGetResponse(
            status_code=500, customer_id=customer_id, errors=str(e)
        )


@router.put("/wallet/{customer_id}/charge")
async def charge_wallet(customer_id: str, amount: float = Body(..., ge=0)):
    try:
        if customer_id not in wallets:
            return WalletChargeResponse(
                status_code=404, customer_id=customer_id, amount=amount
            )

        wallets[customer_id].amount += amount
        return WalletChargeResponse(
            status_code=200,
            customer_id=customer_id,
            amount=amount,
            new_balance=wallets[customer_id].amount,
        )
    except Exception as e:
        return WalletChargeResponse(
            status_code=500, customer_id=customer_id, errors=str(e), amount=-1
        )


@router.put("/wallet/{customer_id}/deduct")
async def deduct_wallet(customer_id: str, amount: float = Body(..., ge=0)):
    try:
        if customer_id not in wallets:
            return WalletDeductResponse(
                status_code=404, customer_id=customer_id, amount=amount
            )

        if wallets[customer_id].amount < amount:
            return WalletDeductResponse(
                status_code=400, customer_id=customer_id, amount=amount
            )

        wallets[customer_id].amount -= amount
        return WalletDeductResponse(
            status_code=200,
            customer_id=customer_id,
            amount=amount,
            new_balance=wallets[customer_id].amount,
        )
    except Exception as e:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
