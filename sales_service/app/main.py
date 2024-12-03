from service import process_purchase, get_purchases
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/api/v1/sales/get")
def fetch_all_purchases():
    """
    Fetches all purchase records from the database.

    :return: A list of purchase records.
    :rtype: List[dict]
    """

    return get_purchases()

@app.post("/api/v1/sales/purchase/{customer_username}/{good_id}")
def purchase_good(customer_username: str, good_id: int):
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
