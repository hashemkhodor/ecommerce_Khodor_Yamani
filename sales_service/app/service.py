import httpx
from app.models import Purchase
from app.database import record_purchase

# URL for communicating between services
INVENTORY_SERVICE_URL = "http://inventory_service:8000/api/v1/inventory"
CUSTOMER_SERVICE_URL = "http://customer_service:8000/api/v1/customer"


def fetch_good_details(good_id: int):
    with httpx.Client() as client:
        response = client.get(f"{INVENTORY_SERVICE_URL}/get/{good_id}")
    if response.status_code == 404:
        raise ValueError(f"Good with ID '{good_id}' not found")
    elif response.status_code != 200:
        raise ValueError("Failed to fetch good details")
    return response.json()


def deduct_wallet_balance(customer_username: str, amount: float):
    with httpx.Client() as client:
        response = client.put(
            f"{CUSTOMER_SERVICE_URL}/wallet/{customer_username}/deduct",
            json={"amount": amount},
        )
    if response.status_code == 404:
        raise ValueError(f"Customer '{customer_username}' not found in the database")
    elif response.status_code != 400:
        raise ValueError("Amount not enough")
    elif response.status_code != 200:
        raise ValueError("Failed to deduct wallet balance")
    return response.json()


def deduct_inventory(good_id: int):
    with httpx.Client() as client:
        response = client.put(f"{INVENTORY_SERVICE_URL}/deduct/{good_id}")
    if response.status_code == 404:
        raise ValueError(f"Good with ID '{good_id}' not found")
    elif response.status_code == 400:
        raise ValueError("Stock already zero")
    elif response.status_code != 200:
        raise ValueError("Failed to deduct inventory")
    return response.json()


def process_purchase(customer_username: str, good_id: int):
    try:
        good = fetch_good_details(good_id)
        price = good["price"]

        deduct_wallet_balance(customer_username, price)
        deduct_inventory(good_id)

        purchase = Purchase(
            good_id=good_id,
            customer_id=customer_username,
            amount_deducted=price,
        )
        record_purchase(purchase)

        return {"message": "Purchase successful"}
    
    except ValueError as e:
        raise ValueError(str(e))
