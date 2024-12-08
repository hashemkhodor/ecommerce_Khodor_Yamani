import os
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from starlette import status

from app.auth import create_access_token, decode_access_token
from app.models import ReviewTable
from app.schemas import (
    BaseCustomResponse,
    DeleteReviewResponse,
    GetReviewsResponse,
    LoginRequest,
    ModerateReviewsResponse,
    PostReviewRequest,
    PostReviewResponse,
    PutReviewRequest,
    PutReviewResponse,
    Review,
)

security = HTTPBearer()
# Define router
router = APIRouter(prefix="/reviews", tags=["Reviews Management"])

load_dotenv()

db: ReviewTable = ReviewTable(
    url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY")
)


@router.post("/submit")
async def submit_review(review: PostReviewRequest):
    """
    Submits a review for an item.

    :param review: The review details.
    :type review: PostReviewRequest
    :return: Response containing the submission status.
    :rtype: PostReviewResponse
    """

    try:

        status_customer_and_item: int = db.customer_and_item_exist(
            review.customer_id, review.item_id
        )
        if status_customer_and_item != status.HTTP_200_OK:
            return PostReviewResponse(
                status_code=status_customer_and_item, review_schema=review
            )

        if db.get_review(item_id=review.item_id, customer_id=review.customer_id):
            return PostReviewResponse(
                status_code=status.HTTP_409_CONFLICT, review_schema=review
            )
        new_review: Review = Review(**review.model_dump(), flagged="needs_approval")
        if db.submit_review(review=new_review):
            return PostReviewResponse(
                status_code=status.HTTP_200_OK, review_schema=review
            )

        return PostReviewResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            review_schema=review,
            errors="Could not submit review",
        )

    except Exception as e:
        return PostReviewResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            review_schema=review,
            errors=str(e),
        )


@router.put("/update")
async def update_review(updated_review: PutReviewRequest):
    """
    Updates an existing review.

    :param updated_review: The updated review details.
    :type updated_review: PutReviewRequest
    :return: Response containing the update status.
    :rtype: PutReviewResponse
    """

    try:
        stored_review: Optional[list[Review]] = db.get_review(
            item_id=updated_review.item_id, customer_id=updated_review.customer_id
        )
        if not stored_review:
            return PutReviewResponse(
                status_code=status.HTTP_404_NOT_FOUND, review_schema=updated_review
            )

        updated_data = stored_review[0].model_dump()
        if updated_review.model_dump(exclude_unset=True).items():
            for _key, value in updated_review.model_dump(exclude_unset=True).items():
                updated_data[_key] = value
        else:
            return PutReviewResponse(
                status_code=status.HTTP_202_ACCEPTED, review_schema=updated_review
            )

        if not db.update_review(review=Review.model_validate(updated_data)):
            return PutReviewResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                review_schema=updated_review,
                errors="Failed to update review",
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
async def delete_review(customer_id: str, item_id: int):
    """
    Deletes a review.

    :param customer_id: The ID of the customer who submitted the review.
    :type customer_id: str
    :param item_id: The ID of the item being reviewed.
    :type item_id: int
    :return: Response containing the deletion status.
    :rtype: DeleteReviewResponse
    """

    try:

        if not db.get_review(item_id=item_id, customer_id=customer_id):
            return DeleteReviewResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                customer_id=customer_id,
                item_id=item_id,
            )
        # if not db
        if db.delete_review(item_id=item_id, customer_id=customer_id):
            return DeleteReviewResponse(
                status_code=status.HTTP_200_OK, customer_id=customer_id, item_id=item_id
            )

        raise Exception("Failed to delete review. Database Error.")

    except Exception as e:
        return DeleteReviewResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            customer_id=customer_id,
            item_id=item_id,
            errors=str(e),
        )


async def get_generic_review(
    item_id: Optional[int] = None, customer_id: Optional[str] = None
) -> GetReviewsResponse:
    """
    Retrieves reviews based on the provided filters.

    :param item_id: The ID of the item to filter reviews by (optional).
    :type item_id: Optional[int]
    :param customer_id: The ID of the customer to filter reviews by (optional).
    :type customer_id: Optional[str]
    :return: A response containing the retrieved reviews.
    :rtype: GetReviewsResponse
    """

    assert item_id or customer_id, "Invalid Call"
    try:
        filters: dict = {}
        if item_id:
            filters["item_id"] = item_id
        if customer_id:
            filters["customer_id"] = customer_id

        reviews: Optional[list[Review]] = db.get_reviews(**filters)
        if reviews is None:
            return GetReviewsResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                reviews=reviews,
                item_id=item_id,
                customer_id=customer_id,
                errors="Database Error",
            )
        return GetReviewsResponse(
            status_code=status.HTTP_200_OK,
            reviews=reviews,
            item_id=item_id,
            customer_id=customer_id,
        )
    except Exception as e:
        logger.exception(e)
        return GetReviewsResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            item_id=item_id,
            errors=str(e),
        )


@router.get("/item/{item_id}")
async def get_item_review(item_id: int):
    """
    Retrieves reviews for a specific item.

    :param item_id: The ID of the item.
    :type item_id: int
    :return: A response containing the retrieved reviews.
    :rtype: GetReviewsResponse
    """
    return await get_generic_review(item_id=item_id)


@router.get("/customer/{customer_id}")
async def get_customer_review(customer_id: str):
    """
    Retrieves all reviews submitted by a specific customer.

    :param customer_id: The ID of the customer whose reviews to retrieve.
    :type customer_id: str
    :return: A response containing the retrieved reviews.
    :rtype: GetReviewsResponse
    """

    return await get_generic_review(customer_id=customer_id)


@router.get("/details")
async def get_details(customer_id: str, item_id: int):
    """
    Retrieves details of a specific review based on the customer and item IDs.

    :param customer_id: The ID of the customer who submitted the review.
    :type customer_id: str
    :param item_id: The ID of the item being reviewed.
    :type item_id: int
    :return: A response containing the review details.
    :rtype: GetReviewsResponse
    """

    return await get_generic_review(item_id=item_id, customer_id=customer_id)


@router.post("/auth/login")
async def login(credentials: LoginRequest):
    """
    Authenticates a user and generates a JWT token.

    :param credentials: The login credentials (username and password).
    :type credentials: LoginRequest
    :return: A response containing the JWT token if login is successful.
    :rtype: BaseCustomResponse
    :raises HTTPException: If the username or password is invalid or if an error occurs.
    """

    try:
        user = (
            db.client.table("customer")
            .select("*")
            .eq("username", credentials.username)
            .eq("password", credentials.password)
            .execute()
        )

        if not user.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Username or password is invalid",
            )
        return BaseCustomResponse(
            status_code=status.HTTP_200_OK,
            data={"token": create_access_token(user.data[0])},
            message="Successfully logged in",
        )

    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/moderate", dependencies=[Depends(security)])
async def moderate(
    customer_id: str,
    item_id: int,
    new_flag: Literal["flagged", "approved", "needs_approval"],
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Moderates a review by updating its flagged status.

    :param customer_id: The ID of the customer who submitted the review.
    :type customer_id: str
    :param item_id: The ID of the item being reviewed.
    :type item_id: int
    :param new_flag: The new flag status for the review. Must be one of ["flagged", "approved", "needs_approval"].
    :type new_flag: Literal["flagged", "approved", "needs_approval"]
    :param credentials: The authentication credentials of the moderator.
    :type credentials: HTTPAuthorizationCredentials
    :return: A response indicating the success or failure of the moderation operation.
    :rtype: ModerateReviewsResponse
    :raises HTTPException: If the user does not have the necessary permissions or if an error occurs.
    """

    try:
        user: dict | str = decode_access_token(credentials.credentials)
        print(user)
        if isinstance(user, str) or user.get("role") and user.get("role") == "customer":
            return ModerateReviewsResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                customer_id=customer_id,
                item_id=item_id,
                new_flag=new_flag,
                errors=(
                    user
                    if isinstance(user, str)
                    else "User don't have the permission to perform this action"
                ),
            )

        customer_item_exist_status: int = db.customer_and_item_exist(
            customer_id=customer_id, item_id=item_id
        )
        if customer_item_exist_status != 200:
            return ModerateReviewsResponse(
                status_code=customer_item_exist_status,
                customer_id=customer_id,
                item_id=item_id,
                new_flag=new_flag,
            )

        review: list[Review] = db.get_review(customer_id=customer_id, item_id=item_id)
        if review is None or len(review) == 0:
            return ModerateReviewsResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                customer_id=customer_id,
                item_id=item_id,
                new_flag=new_flag,
            )
        review: Review = review[0]

        new_review: list[Review] = db.update_review(
            review=Review(**review.model_dump(exclude={"flagged"}), flagged=new_flag)
        )

        if new_review is None or len(new_review) == 0:
            return ModerateReviewsResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                customer_id=customer_id,
                item_id=item_id,
                new_flag=new_flag,
                errors="Database Error",
            )
        return ModerateReviewsResponse(
            status_code=status.HTTP_200_OK,
            customer_id=customer_id,
            item_id=item_id,
            new_flag=new_flag,
            review=new_review[0],
        )
    except Exception as e:
        logger.error(e)
        return ModerateReviewsResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            customer_id=customer_id,
            item_id=item_id,
            new_flag=new_flag,
            errors=str(e),
        )


app = FastAPI(
    title="Ecommerce Review Router",
    description="Router for all reviews related stuff",
    version="1.0.0",
    debug=True,
)
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is operational.
    :return: A simple status message.
    :rtype: dict
    """
    try:
        # Perform a basic database operation to verify connectivity
        db.customer_and_item_exist("sure", 1)
        return {"status": "OK", "db_status": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "ERROR", "db_status": "disconnected", "error": str(e)}