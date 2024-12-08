import os

import httpx
from app.database import SalesTable
from app.models import Purchase
from dotenv import load_dotenv
from fastapi import HTTPException
from loguru import logger

# URL for communicating between services
INVENTORY_SERVICE_URL = "http://127.0.0.1:8002/api/v1/inventory"
CUSTOMER_SERVICE_URL = "http://127.0.0.1:8001/api/v1/customer"

load_dotenv()
db_sale: SalesTable = SalesTable(
    url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY")
)


def fetch_good_details(good_id: int):
    """
    Fetches details of a specific good from the inventory service.

    :param good_id: The ID of the good to fetch details for.
    :type good_id: int
    :return: Details of the good as a dictionary.
    :rtype: dict
    :raises ValueError: If the good is not found or the request fails.
    """

    logger.info(f"Good details fetched: {good_id}")

    with httpx.Client() as client:
        logger.info(f"IN CLIENT: {good_id}")
        response = client.get(f"{INVENTORY_SERVICE_URL}/{good_id}")
        # logger.info(response.json())
        logger.info(f"AFTER CLIENT: {good_id}")
        if response.status_code == 404:
            logger.info(f"IN 404: {response.status_code}")
            raise ValueError(f"Good with ID '{good_id}' not found")
        elif response.status_code != 200:
            logger.info(f"IN 200: {response.status_code}")
            raise ValueError("Failed to fetch good details")
        return response.json()


def deduct_wallet_balance(customer_username: str, amount: float):
    """
    Deducts the specified amount from a customer's wallet.

    :param customer_username: The username of the customer.
    :type customer_username: str
    :param amount: The amount to deduct from the wallet.
    :type amount: float
    :return: Response from the customer service.
    :rtype: dict
    :raises ValueError: If the customer is not found, insufficient funds, or the request fails.
    """

    with httpx.Client() as client:
        response = client.put(
            f"{CUSTOMER_SERVICE_URL}/wallet/{customer_username}/deduct", json=amount
        )
        logger.info(response.status_code)
        if response.status_code == 404:
            raise ValueError(
                f"Customer '{customer_username}' not found in the database"
            )
        elif response.status_code == 400:
            raise ValueError("Amount not enough")
        elif response.status_code != 200:
            raise ValueError("Failed to deduct wallet balance")
        return response.json()


def deduct_inventory(good_id: int):
    """
    Deducts one unit from the inventory stock of a specific good.

    :param good_id: The ID of the good to deduct stock for.
    :type good_id: int
    :return: Response from the inventory service.
    :rtype: dict
    :raises ValueError: If the good is not found, stock is zero, or the request fails.
    """

    with httpx.Client() as client:
        logger.info(f"IN DEDUCT INV: {good_id}")

        response = client.put(f"{INVENTORY_SERVICE_URL}/deduct/{good_id}")
        logger.info(f"RESPONSE: {response.status_code}")

        if response.status_code == 404:
            raise ValueError(f"Good with ID '{good_id}' not found")
        elif response.status_code == 400:
            raise ValueError("Stock already zero")
        elif response.status_code != 200:
            raise ValueError("Failed to deduct inventory")
        return response.json()


def process_purchase(customer_username: str, good_id: int):
    """
    Processes the purchase of a good by a customer.

    :param customer_username: The username of the customer making the purchase.
    :type customer_username: str
    :param good_id: The ID of the good being purchased.
    :type good_id: int
    :return: A success message confirming the purchase.
    :rtype: dict
    :raises ValueError: If any error occurs during the purchase process.
    """

    try:
        logger.info(f"Processing purchase for {customer_username} and good {good_id}")
        good = fetch_good_details(good_id)
        price = good["price"]

        deduct_wallet_balance(customer_username, price)

        deduct_inventory(good_id)

        purchase = Purchase(
            good_id=good_id,
            customer_id=customer_username,
            amount_deducted=price,
        )
        db_sale.record_purchase(purchase)
        logger.info(f"Purchase recorded: {purchase}")

        return {"message": "Purchase successful"}

    except ValueError as e:
        raise ValueError(str(e))


def get_purchases():
    """
    Retrieves all purchase records from the database.

    :return: A list of purchase records.
    :rtype: list[dict]
    :raises HTTPException: If the database query fails.
    """

    try:
        purchases = db_sale.get_purchases()
        return [
            {
                "id": purchase["id"],
                "good_id": purchase["good_id"],
                "customer_id": purchase["customer_id"],
                "amount_deducted": purchase["amount_deducted"],
                "time": purchase["time"],
            }
            for purchase in purchases
        ]
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
