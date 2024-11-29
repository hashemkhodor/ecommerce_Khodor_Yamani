from fastapi import FastAPI, HTTPException
from app.models import Good, GoodUpdate
from app.database import get_db_connection
from app.service import add_good, update_good, get_good, deduct_good

app = FastAPI()

@app.post("/api/v1/inventory/add")
def add_good_endpoint(good: Good):
    connection = get_db_connection()
    try:
        return add_good(connection, good)
    finally:
        connection.close()

@app.put("/api/v1/inventory/update/{good_id}")
def update_good_endpoint(good_id: int, good: GoodUpdate):
    connection = get_db_connection()
    try:
        return update_good(connection, good_id, good)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        connection.close()

@app.get("/api/v1/inventory/{good_id}")
def get_good_endpoint(good_id: int):
    connection = get_db_connection()
    try:
        return get_good(connection, good_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        connection.close()

@app.put("/api/v1/inventory/deduct/{good_id}")
def deduct_good_endpoint(good_id: int):
    connection = get_db_connection()
    try:
        return deduct_good(connection, good_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        connection.close()
