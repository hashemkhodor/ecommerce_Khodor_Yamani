from app.database import get_purchases
from app.service import process_purchase
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/api/v1/sales/get")
def fetch_all_purchases():
    try:
        purchases = get_purchases()
        return [
            {
                "id": purchase["id"],
                "good_id": purchase["good_id"],
                "user_id": purchase["user_id"],
                "amount_deducted": purchase["amount_deducted"],
                "time": purchase["time"],
            }
            for purchase in purchases
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sales/purchase")
def purchase_good(customer_username: str, good_id: int):
    try:
        return process_purchase(customer_username, good_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
