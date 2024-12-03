from fastapi import FastAPI, HTTPException
from loguru import logger
from app.models import Good, GoodUpdate
from app.service import add_good, deduct_good, get_good, update_good

app = FastAPI()


@app.post("/api/v1/inventory/add")
def add_good_endpoint(good: Good):
    """
    Endpoint to add a new item to the inventory.

    Args:
        good (Good): The item details to be added.

    Returns:
        dict: The details of the added item.

    Raises:
        HTTPException: If an error occurs while adding the item.
    """

    try:
        return add_good(good)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/inventory/update/{good_id}")
def update_good_endpoint(good_id: int, good: GoodUpdate):
    """
    Endpoint to update an existing inventory item.

    Args:
        good_id (int): The ID of the item to update.
        good (GoodUpdate): The updated fields for the item.

    Returns:
        dict: The details of the updated item.

    Raises:
        HTTPException: If the item is not found or an error occurs while updating.
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
    Endpoint to retrieve an inventory item by its ID.

    Args:
        good_id (int): The ID of the item to retrieve.

    Returns:
        dict: The details of the retrieved item.

    Raises:
        HTTPException: If the item is not found or an error occurs while retrieving.
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
    Endpoint to deduct one unit from the stock of an inventory item.

    Args:
        good_id (int): The ID of the item to deduct stock from.

    Returns:
        dict: The updated details of the item after deduction.

    Raises:
        HTTPException: If the stock is insufficient or an error occurs while deducting.
    """

    try:
        return deduct_good(good_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)
