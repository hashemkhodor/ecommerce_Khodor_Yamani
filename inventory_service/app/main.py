from fastapi import FastAPI, HTTPException
from models import Good, GoodUpdate
from service import add_good, deduct_good, get_good, update_good
from loguru import logger

app = FastAPI()


@app.post("/api/v1/inventory/add")
def add_good_endpoint(good: Good):
    """
    Adds a new inventory item.

    :param good: The details of the item to be added.
    :type good: Good
    :return: The response from the service layer after adding the item.
    :rtype: dict
    :raises HTTPException: If an error occurs during the addition process.
    """

    try:
        return add_good(good)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/inventory/update/{good_id}")
def update_good_endpoint(good_id: int, good: GoodUpdate):
    """
    Updates an existing inventory item.

    :param good_id: The ID of the item to be updated.
    :type good_id: int
    :param good: The updated details of the item.
    :type good: GoodUpdate
    :return: The response from the service layer after updating the item.
    :rtype: dict
    :raises HTTPException: If the item is not found or if an error occurs during the update process.
    """

    try:
        return update_good(good_id, good)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/inventory/{good_id}")
def get_good_endpoint(good_id: int):
    """
    Retrieves an inventory item by its ID.

    :param good_id: The ID of the item to be retrieved.
    :type good_id: int
    :return: The details of the requested inventory item.
    :rtype: dict
    :raises HTTPException: If the item is not found or if an error occurs during retrieval.
    """

    try:
        return get_good(good_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/inventory/deduct/{good_id}")
def deduct_good_endpoint(good_id: int):
    """
    Deducts one unit from an inventory item by its ID.

    :param good_id: The ID of the item to be deducted.
    :type good_id: int
    :return: The response from the service layer after deduction.
    :rtype: dict
    :raises HTTPException: If the stock is insufficient or if an error occurs during deduction.
    """

    try:
        return deduct_good(good_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


