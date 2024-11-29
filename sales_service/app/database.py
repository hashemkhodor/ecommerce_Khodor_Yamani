import sqlite3
from sqlite3 import Connection
from app.models import Purchase

DB_NAME = "sales.db"

def create_tables():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        good_id INTEGER NOT NULL,
        customer_id TEXT NOT NULL,
        amount_deducted REAL NOT NULL,
        time TEXT NOT NULL
    )
    """)

    connection.commit()
    connection.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def record_purchase(connection: Connection, purchase: Purchase):
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO purchases (good_id, customer_id, amount_deducted, time)
    VALUES (?, ?, ?, ?)
    """, (purchase.good_id, purchase.customer_id, purchase.amount_deducted, purchase.time))
    connection.commit()

def get_purchases(connection: Connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM purchases")
    return cursor.fetchall()

create_tables()