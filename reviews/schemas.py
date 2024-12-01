from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class Review(BaseModel):
    customer_id: str
    item_id: str
    rating: int = Field(
        ..., ge=1, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: str
    time: Optional[datetime] = Field(None)
    flagged: Literal["flagged", "approved", "needs_approval"]


class PostReviewRequest(BaseModel):
    customer_id: str
    item_id: str
    rating: int = Field(
        ..., ge=1, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: str


class PutReviewRequest(BaseModel):
    customer_id: str
    item_id: str
    rating: Optional[int] = Field(
        ..., ge=1, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: Optional[str] = None


# class DeleteReviewRequest(BaseModel):
#     user_id: str
#     item_id: str


class ModerateRequest(BaseModel):
    """ """

    customer_id: str
    item_id: str

    flag: Literal["flagged", "approved", "needs_approval"]


class BaseCustomResponse(JSONResponse):
    """
    Base response class to handle shared logic for custom responses.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        data: Optional[Any] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        content = {"message": message}
        if data is not None:
            content["data"] = data
        if notes:
            content["notes"] = notes
        if errors:
            content["errors"] = errors
        super().__init__(content=content, status_code=status_code)


class PostReviewResponse(BaseCustomResponse):
    """
    Response for customer registration.
    """

    def __init__(
        self,
        status_code: int,
        review_schema: PostReviewRequest,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_200_OK:
            message = (
                f"Posted {review_schema.customer_id}'s review for {review_schema.item_id} successfully."
                f"Waiting for admin review to be completed ..."
            )

        elif status_code == status.HTTP_409_CONFLICT:
            message = (
                f"{review_schema.customer_id}'s review for {review_schema.item_id} already exists. If you want to update"
                f"send a put request instead of post."
            )

        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try posting review again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code, message=message, notes=notes, errors=errors
        )


class PutReviewResponse(BaseCustomResponse):
    """
    Response for customer registration.
    """

    def __init__(
        self,
        status_code: int,
        review_schema: PutReviewRequest,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_200_OK:
            if review_schema is None:
                raise ValueError(
                    "Updated review data must be provided for a 200 OK status"
                )
            message = f"Updated {review_schema.customer_id}'s review for {review_schema.item_id} successfully."
            data = review_schema.model_dump()
        elif status_code == status.HTTP_202_ACCEPTED:
            message = (
                f"{review_schema.customer_id}'s review for {review_schema.item_id} update request processed,"
                f" but no new data available"
            )
            data = None
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"{review_schema.customer_id}'s review for {review_schema.item_id} not found"
            data = None
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try updating again later"
            data = None
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            data=data,
            notes=notes,
            errors=errors,
        )


class DeleteReviewResponse(BaseCustomResponse):
    """
    Response for customer registration.
    """

    def __init__(
        self,
        status_code: int,
        item_id: str,
        customer_id: str,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_200_OK:
            message = f"Deleted review successfully."
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"{customer_id}'s review for {item_id} not found"
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try deleting again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            notes=notes,
            errors=errors,
        )
