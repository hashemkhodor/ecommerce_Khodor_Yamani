from app.service import get_purchases, process_purchase
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify that the service is operational.

    :return: A simple status message.
    :rtype: dict
    """
    try:
        # Perform a simple database operation to ensure connectivity
        purchases = get_purchases()
        return {
            "status": "OK",
            "db_status": "connected",
            "records_found": len(purchases),
        }
    except Exception as e:
        return {"status": "ERROR", "db_status": "disconnected", "error": str(e)}


@app.get("/api/v1/sales/get")
async def fetch_all_purchases():
    """
    Fetches all purchase records from the database.

    :return: A list of purchase records.
    :rtype: List[dict]
    """
    try:
        return get_purchases()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/sales/purchase/{customer_username}/{good_id}")
async def purchase_good(customer_username: str, good_id: int):
    """
    Processes the purchase of a good by a customer.

    :param customer_username: The username of the customer making the purchase.
    :type customer_username: str
    :param good_id: The ID of the good being purchased.
    :type good_id: int
    :return: A confirmation of the successful purchase or an error message.
    :rtype: dict
    :raises HTTPException: If a ValueError occurs (status code 400) or a general exception occurs (status code 500).
    """

    try:
        return process_purchase(customer_username, good_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
