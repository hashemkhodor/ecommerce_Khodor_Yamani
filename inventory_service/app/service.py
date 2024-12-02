"""
from database import (
    add_good_to_db,
    deduct_good_from_db,
    get_good_from_db,
    update_good_in_db,
)
"""
import os
from database import InventoryTable
from models import Good, GoodUpdate
from dotenv import load_dotenv

load_dotenv()
db_inv: InventoryTable = InventoryTable(
    url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY")
)

def add_good(good: Good):
    db_inv.add_good_to_db(good)
    return {"message": "Good added successfully"}


def update_good(good_id: int, good_update: GoodUpdate):
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
    good = db_inv.get_good_from_db(good_id)
    if not good:
        raise ValueError("Good not found")
    return good  # Supabase already returns a dictionary


def deduct_good(good_id: int):
    try:
        db_inv.deduct_good_from_db(good_id)
    except ValueError as e:
        raise ValueError(str(e))
    return {"message": "Stock deducted successfully"}
