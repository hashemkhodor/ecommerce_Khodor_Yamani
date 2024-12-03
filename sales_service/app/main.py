from service import process_purchase, get_purchases
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/api/v1/sales/get")
def fetch_all_purchases():
    return get_purchases()

@app.post("/api/v1/sales/purchase/{customer_username}/{good_id}")
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
