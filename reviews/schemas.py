from typing import Any, Literal, Optional

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class Review(BaseModel):
    customer_id: str
    item_id: int
    rating: int = Field(
        ..., ge=0, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: str
    time: Optional[str] = Field(None)
    flagged: Literal["flagged", "approved", "needs_approval"]


class LoginRequest(BaseModel):
    username: str
    password: str


class PostReviewRequest(BaseModel):
    customer_id: str
    item_id: int
    rating: int = Field(
        ..., ge=0, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: str


class PutReviewRequest(BaseModel):
    customer_id: str
    item_id: int
    rating: Optional[int] = Field(
        ..., ge=0, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: Optional[str] = None


# class DeleteReviewRequest(BaseModel):
#     user_id: str
#     item_id: str


class ModerateRequest(BaseModel):
    """ """

    customer_id: str
    item_id: int

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


class LoginResponse(BaseCustomResponse):
    def __init__(
        self,
        status_code: int,
        credentials_schema: LoginRequest,
        token: Optional[str] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        if status_code == status.HTTP_200_OK:
            # Successful login
            data = {"token": token}
            message = f"User '{credentials_schema.username}' logged in successfully."
        elif status_code == status.HTTP_400_BAD_REQUEST:
            # Bad request (e.g., missing fields, invalid data)
            message = "Invalid login request. Please check the username and password."
            data = None
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            # Unauthorized access (e.g., incorrect credentials)
            message = "Unauthorized. Incorrect username or password."
            data = None
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            # Server error
            message = "Internal Server Error. Please try logging in again later."
            data = None
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            notes=notes,
            errors=errors,
            data=data,
        )


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
                f" Waiting for admin review to be completed ..."
            )

        elif status_code == status.HTTP_400_BAD_REQUEST:
            message = f"Either customer '{review_schema.customer_id}' or item with id '{review_schema.item_id}' doesn't exist."
        elif status_code == status.HTTP_409_CONFLICT:
            message = (
                f"{review_schema.customer_id}'s review for {review_schema.item_id} already exists. If you want to update"
                f" send a put request instead of post."
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
        item_id: int,
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


class GetReviewsResponse(BaseCustomResponse):
    """
    Response for customer registration.
    """

    def __init__(
        self,
        status_code: int,
        item_id: Optional[int] = None,
        customer_id: Optional[str] = None,
        reviews: Optional[list[Review]] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        assert (item_id is not None) or (
            customer_id is not None
        ), "You must provide either item_id or customer_id"
        data: Optional[list[dict]] = None

        if status_code == status.HTTP_200_OK:
            if item_id and customer_id:
                identifier_message = (
                    f"for item_id {item_id} and customer_id {customer_id}"
                )
            elif item_id:
                identifier_message = f"for item_id {item_id}"
            elif customer_id:
                identifier_message = f"for customer_id {customer_id}"
            else:
                identifier_message = ""

            message = f"Fetched reviews successfully {identifier_message}."
            assert (
                reviews is not None
            ), "You must provide reviews if status code is good"
            data = [review.model_dump() for review in reviews]

        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try deleting again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            notes=notes,
            errors=errors,
            data=data,
        )


class ModerateReviewsResponse(BaseCustomResponse):
    """
    Response for customer registration.
    """

    def __init__(
        self,
        status_code: int,
        item_id: int,
        customer_id: str,
        new_flag: str,
        review: Optional[Review] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        data: Optional[dict] = None

        if status_code == status.HTTP_200_OK:
            if item_id and customer_id:
                identifier_message = (
                    f"for item_id {item_id} and customer_id {customer_id}"
                )
            elif item_id:
                identifier_message = f"for item_id {item_id}"
            elif customer_id:
                identifier_message = f"for customer_id {customer_id}"
            else:
                identifier_message = ""

            message = f"Moderate review successfully {identifier_message}. Changed it from {review.flagged} to {new_flag}"
            assert review is not None, "You must provide reviews if status code is good"
            data = {"review": review.model_dump()}

        elif status_code == status.HTTP_400_BAD_REQUEST:
            message = f"Customer '{customer_id}' or item with id '{item_id}' not found"
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            message = f"Invalid Bearer Token"
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = f"{customer_id}'s review for {item_id} not found"
        elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            message = "Internal Server Error. Please try moderating again later"
        else:
            raise ValueError(f"Unexpected status code: {status_code}")

        super().__init__(
            status_code=status_code,
            message=message,
            notes=notes,
            errors=errors,
            data=data,
        )
