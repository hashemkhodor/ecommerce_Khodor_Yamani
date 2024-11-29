import sqlite3
from sqlite3 import Connection
from app.models import Good

DB_NAME = "inventory.db"

# create table/connections
def create_tables():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT NOT NULL,
        count INTEGER NOT NULL
    )
    """)
    connection.commit()
    connection.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# database manipulation functions
def add_good_to_db(connection: Connection, good: Good):
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO inventory (name, category, price, description, count)
    VALUES (?, ?, ?, ?, ?)
    """, (good.name, good.category.value, good.price, good.description, good.count))
    connection.commit()

def update_good_in_db(connection: Connection, good_id: int, updated_good: dict):
    cursor = connection.cursor()
    cursor.execute("""
    UPDATE inventory
    SET name = ?, category = ?, price = ?, description = ?, count = ?
    WHERE id = ?
    """, (
        updated_good["name"],
        updated_good["category"],
        updated_good["price"],
        updated_good["description"],
        updated_good["count"],
        good_id,
    ))
    connection.commit()

def get_good_from_db(connection: Connection, good_id: int):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inventory WHERE id = ?", (good_id,))
    return cursor.fetchone()

def deduct_good_from_db(connection: Connection, good_id: int):
    cursor = connection.cursor()
    cursor.execute("""
    UPDATE inventory
    SET count = count - 1
    WHERE id = ? AND count > 0
    """, (good_id,))
    if cursor.rowcount == 0:
        raise ValueError("Existing stock was already zero!")
    connection.commit()

create_tables()
