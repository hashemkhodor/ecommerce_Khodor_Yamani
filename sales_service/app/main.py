from fastapi import FastAPI, HTTPException
from app.database import get_db_connection, get_purchases
from app.service import process_purchase

app = FastAPI()

@app.get("/api/v1/sales/get")
def fetch_all_purchases():
    connection = get_db_connection()
    try:
        purchases = get_purchases(connection)
        # format raw database rows into list of dict
        return [
            {
                "id": purchase[0],
                "good_id": purchase[1],
                "customer_id": purchase[2],
                "amount_deducted": purchase[3],
                "time": purchase[4],
            }
            for purchase in purchases
        ]
    finally:
        connection.close()


@app.post("/api/v1/sales/purchase")
def purchase_good(customer_username: str, good_id: int):
    connection = get_db_connection()
    try:
        return process_purchase(connection, customer_username, good_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()