from app.models import Good, GoodUpdate
from app.database import (
    add_good_to_db,
    update_good_in_db,
    get_good_from_db,
    deduct_good_from_db,
)
from sqlite3 import Connection

def add_good(connection: Connection, good: Good):
    add_good_to_db(connection, good)
    return {"message": "Good added successfully"}

def update_good(connection: Connection, good_id: int, good_update: GoodUpdate):
    existing_good = get_good_from_db(connection, good_id)
    if not existing_good:
        raise ValueError("Good not found")

    # updated values
    updated_good = {
        "name": good_update.name or existing_good[1],
        "category": good_update.category.value if good_update.category else existing_good[2],
        "price": good_update.price if good_update.price is not None else existing_good[3],
        "description": good_update.description or existing_good[4],
        "count": good_update.count if good_update.count is not None else existing_good[5],
    }

    update_good_in_db(connection, good_id, updated_good)
    return {"message": "Good updated successfully"}

def get_good(connection: Connection, good_id: int):
    good = get_good_from_db(connection, good_id)
    if not good:
        raise ValueError("Good not found")
    return {
        "id": good[0],
        "name": good[1],
        "category": good[2],
        "price": good[3],
        "description": good[4],
        "count": good[5],
    }

def deduct_good(connection: Connection, good_id: int):
    try:
        deduct_good_from_db(connection, good_id)
    except ValueError as e:
        raise ValueError(str(e))
    return {"message": "Stock deducted successfully"}
