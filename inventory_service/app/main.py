from fastapi import FastAPI, HTTPException
from models import Good, GoodUpdate
from service import add_good, deduct_good, get_good, update_good
from loguru import logger

app = FastAPI()


@app.post("/api/v1/inventory/add")
def add_good_endpoint(good: Good):
    try:
        return add_good(good)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/inventory/update/{good_id}")
def update_good_endpoint(good_id: int, good: GoodUpdate):
    try:
        return update_good(good_id, good)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/inventory/{good_id}")
def get_good_endpoint(good_id: int):
    try:
        return get_good(good_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/inventory/deduct/{good_id}")
def deduct_good_endpoint(good_id: int):
    try:
        return deduct_good(good_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)
