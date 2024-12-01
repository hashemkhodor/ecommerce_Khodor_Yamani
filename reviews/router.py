from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette import status

from customer.schemas import CustomerUpdateResponse
from reviews.schemas import (DeleteReviewResponse, PostReviewRequest,
                             PostReviewResponse, PutReviewRequest,
                             PutReviewResponse, Review)

# Define router
router = APIRouter(prefix="/reviews", tags=["Reviews Management"])

# reviews: dict[tuple[str, str], Review] = {}

reviews: dict[str, dict[str, Review]] = {}


@router.post("/submit")
async def submit_review(review: PostReviewRequest):
    try:

        key1, key2 = review.item_id, review.customer_id
        if key1 not in reviews or key2 not in reviews[key1]:
            return PostReviewResponse(
                status_code=status.HTTP_409_CONFLICT, review_schema=review
            )

        reviews[key1][key2] = Review(
            **review.model_dump(), time=datetime.now(), flagged="needs_approval"
        )
        return PostReviewResponse(status_code=status.HTTP_200_OK, review_schema=review)

    except Exception as e:
        return PostReviewResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            review_schema=review,
            errors=str(e),
        )


@router.put("/update")
async def update_review(updated_review: PutReviewRequest):
    try:
        key: tuple[str, str] = (updated_review.item_id, updated_review.customer_id)
        stored_review = reviews[key]
        updated_data = stored_review.model_dump()
        if updated_review.model_dump(exclude_unset=True).items():
            for _key, value in updated_review.model_dump(exclude_unset=True).items():
                updated_data[_key] = value
        else:
            return PutReviewResponse(
                status_code=status.HTTP_202_ACCEPTED, review_schema=updated_review
            )
        return PutReviewResponse(
            status_code=status.HTTP_200_OK,
            review_schema=updated_review,
        )

    except Exception as e:
        return PutReviewResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            review_schema=updated_review,
            errors=str(e),
        )


@router.delete("/delete")
async def delete_review(customer_id: str, item_id: str):
    try:
        key: tuple[str, str] = (item_id, customer_id)
        if key not in reviews:
            return DeleteReviewResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                customer_id=customer_id,
                item_id=item_id,
            )
        del reviews[key]
        return DeleteReviewResponse(
            status_code=status.HTTP_200_OK, customer_id=customer_id, item_id=item_id
        )
    except Exception as e:
        return DeleteReviewResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            customer_id=customer_id,
            item_id=item_id,
            errors=str(e),
        )


@router.get("/product/{product_id}")
async def get_review(product_id: str):
    # Get From Database
    pass


@router.get("/customer/{customer_id}")
async def get_customer_review(customer_id: str):
    # Get From Database
    pass


@router.put("/moderate")
async def moderate():
    # Update Database
    pass


@router.get("/details")
async def get_details():
    # Get from database
    pass


app = FastAPI(
    title="Ecommerce Review Router",
    description="Router for all reviews related stuff",
    version="1.0.0",
    debug=True,
)
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
