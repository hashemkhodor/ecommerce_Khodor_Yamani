import os

from app.database import InventoryTable
from app.models import Good, GoodUpdate
from dotenv import load_dotenv

load_dotenv()
db_inv: InventoryTable = InventoryTable(
    url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY")
)


def add_good(good: Good):
    """
    Adds a new inventory item to the database.

    :param good: The `Good` object containing the item details to add.
    :type good: Good
    :return: A success message confirming the item was added.
    :rtype: dict
    :raises Exception: If the database operation fails.
    """

    db_inv.add_good_to_db(good)
    return {"message": "Good added successfully"}


def update_good(good_id: int, good_update: GoodUpdate):
    """
    Updates an existing inventory item in the database.

    :param good_id: The ID of the item to update.
    :type good_id: int
    :param good_update: The fields to update for the item.
    :type good_update: GoodUpdate
    :return: A success message confirming the item was updated.
    :rtype: dict
    :raises ValueError: If the item with the given ID does not exist.
    :raises Exception: If the database operation fails.
    """

    existing_good = db_inv.get_good_from_db(good_id)
    if not existing_good:
        raise ValueError("Good not found")

    # updated values
    updated_good = {
        "name": good_update.name or existing_good["name"],
        "category": (
            good_update.category.value
            if good_update.category
            else existing_good["category"]
        ),
        "price": (
            good_update.price
            if good_update.price is not None
            else existing_good["price"]
        ),
        "description": good_update.description or existing_good["description"],
        "count": (
            good_update.count
            if good_update.count is not None
            else existing_good["count"]
        ),
    }

    db_inv.update_good_in_db(good_id, updated_good)
    return {"message": "Good updated successfully"}


def get_good(good_id: int):
    """
    Retrieves an inventory item by its ID.

    :param good_id: The ID of the item to retrieve.
    :type good_id: int
    :return: The details of the retrieved item.
    :rtype: dict
    :raises ValueError: If the item with the given ID does not exist.
    """

    good = db_inv.get_good_from_db(good_id)
    if not good:
        raise ValueError("Good not found")
    return good  # Supabase already returns a dictionary


def deduct_good(good_id: int):
    """
    Deducts one unit from the stock of an inventory item.

    :param good_id: The ID of the item to deduct stock from.
    :type good_id: int
    :return: A success message confirming the stock was deducted.
    :rtype: dict
    :raises ValueError: If the stock is already zero or the item does not exist.
    :raises Exception: If the database operation fails.
    """

    try:
        db_inv.deduct_good_from_db(good_id)
    except ValueError as e:
        raise ValueError(str(e))
    return {"message": "Stock deducted successfully"}
