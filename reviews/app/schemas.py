from typing import Any, Literal, Optional

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class Review(BaseModel):
    """
    Represents a review submitted by a customer.

    Attributes:
        customer_id (str): The ID of the customer submitting the review.
        item_id (int): The ID of the item being reviewed.
        rating (int): The rating given by the customer, must be between 0 and 5.
        comment (str): The text comment provided by the customer.
        time (Optional[str]): The timestamp of when the review was submitted.
        flagged (Literal["flagged", "approved", "needs_approval"]): The moderation status of the review.
    """

    customer_id: str
    item_id: int
    rating: int = Field(
        ..., ge=0, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: str
    time: Optional[str] = Field(None)
    flagged: Literal["flagged", "approved", "needs_approval"]


class LoginRequest(BaseModel):
    """
    Represents the schema for a login request.

    Attributes:
        username (str): The username of the customer.
        password (str): The password for the customer's account.
    """

    username: str
    password: str


class PostReviewRequest(BaseModel):
    """
    Represents the schema for submitting a new review.

    Attributes:
        customer_id (str): The ID of the customer submitting the review.
        item_id (int): The ID of the item being reviewed.
        rating (int): The rating given by the customer, must be between 0 and 5.
        comment (str): The text comment provided by the customer.
    """

    customer_id: str
    item_id: int
    rating: int = Field(
        ..., ge=0, le=5, description="Rating must be between 1 and 5"
    )  # Enforce range 1-5
    comment: str


class PutReviewRequest(BaseModel):
    """
    Represents the schema for updating an existing review.

    Attributes:
        customer_id (str): The ID of the customer who submitted the review.
        item_id (int): The ID of the item being reviewed.
        rating (Optional[int]): The updated rating, if provided. Must be between 0 and 5.
        comment (Optional[str]): The updated comment, if provided.
    """

    customer_id: str
    item_id: int
    rating: Optional[int] = Field(
        None, ge=0, le=5, description="Rating must be between 1 and 5"
    )
    comment: Optional[str] = None


# class DeleteReviewRequest(BaseModel):
#     user_id: str
#     item_id: str


class ModerateRequest(BaseModel):
    """
    Represents a moderation request for a review.

    Attributes:
        customer_id (str): The ID of the customer whose review is being moderated.
        item_id (int): The ID of the item being reviewed.
        flag (Literal["flagged", "approved", "needs_approval"]): The new moderation status for the review.
    """

    customer_id: str
    item_id: int

    flag: Literal["flagged", "approved", "needs_approval"]


class BaseCustomResponse(JSONResponse):
    """
    Base response class for standardizing API responses.

    Attributes:
        status_code (int): The HTTP status code of the response.
        message (str): A descriptive message about the response.
        data (Optional[Any]): The payload data for the response.
        notes (Optional[str]): Additional notes for the response.
        errors (Optional[str]): Any errors related to the response.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        data: Optional[Any] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the BaseCustomResponse.

        :param status_code: The HTTP status code of the response.
        :type status_code: int
        :param message: A descriptive message for the response.
        :type message: str
        :param data: Optional payload data for the response.
        :type data: Optional[Any]
        :param notes: Optional notes about the response.
        :type notes: Optional[str]
        :param errors: Optional error details.
        :type errors: Optional[str]
        """

        content = {"message": message}
        if data is not None:
            content["data"] = data
        if notes:
            content["notes"] = notes
        if errors:
            content["errors"] = errors
        super().__init__(content=content, status_code=status_code)


class LoginResponse(BaseCustomResponse):
    """
    Response schema for login operations.

    Attributes:
        credentials_schema (LoginRequest): The schema of the login credentials.
        token (Optional[str]): The JWT token generated for the user.
    """

    def __init__(
        self,
        status_code: int,
        credentials_schema: LoginRequest,
        token: Optional[str] = None,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the LoginResponse.

        :param status_code: The HTTP status code of the response.
        :type status_code: int
        :param credentials_schema: The schema of the login credentials.
        :type credentials_schema: LoginRequest
        :param token: The JWT token for the logged-in user.
        :type token: Optional[str]
        :param notes: Optional notes about the response.
        :type notes: Optional[str]
        :param errors: Optional error details.
        :type errors: Optional[str]
        """

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
    Response schema for submitting a new review.

    Attributes:
        review_schema (PostReviewRequest): The schema of the submitted review.
    """

    def __init__(
        self,
        status_code: int,
        review_schema: PostReviewRequest,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the PostReviewResponse.

        :param status_code: The HTTP status code of the response.
        :type status_code: int
        :param review_schema: The schema of the submitted review.
        :type review_schema: PostReviewRequest
        :param notes: Optional notes about the response.
        :type notes: Optional[str]
        :param errors: Optional error details.
        :type errors: Optional[str]
        """

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
    Response schema for updating an existing review.

    Attributes:
        review_schema (PutReviewRequest): The schema of the updated review.
    """

    def __init__(
        self,
        status_code: int,
        review_schema: PutReviewRequest,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the PutReviewResponse.

        :param status_code: The HTTP status code of the response.
        :type status_code: int
        :param review_schema: The schema of the updated review.
        :type review_schema: PutReviewRequest
        :param notes: Optional notes about the response.
        :type notes: Optional[str]
        :param errors: Optional error details.
        :type errors: Optional[str]
        """

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
    Response schema for deleting a review.

    Attributes:
        item_id (int): The ID of the item being reviewed.
        customer_id (str): The ID of the customer whose review is being deleted.
    """

    def __init__(
        self,
        status_code: int,
        item_id: int,
        customer_id: str,
        notes: Optional[str] = None,
        errors: Optional[str] = None,
    ):
        """
        Initializes the DeleteReviewResponse.

        :param status_code: The HTTP status code of the response.
        :type status_code: int
        :param item_id: The ID of the item being reviewed.
        :type item_id: int
        :param customer_id: The ID of the customer whose review is being deleted.
        :type customer_id: str
        :param notes: Optional notes about the response.
        :type notes: Optional[str]
        :param errors: Optional error details.
        :type errors: Optional[str]
        """

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
    Response schema for retrieving reviews.

    Attributes:
        item_id (Optional[int]): The ID of the item being reviewed, if applicable.
        customer_id (Optional[str]): The ID of the customer whose reviews are retrieved, if applicable.
        reviews (Optional[list[Review]]): A list of retrieved reviews.
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
        """
        Initializes the GetReviewsResponse.

        :param status_code: The HTTP status code of the response.
        :type status_code: int
        :param item_id: The ID of the item being reviewed, if applicable.
        :type item_id: Optional[int]
        :param customer_id: The ID of the customer whose reviews are retrieved, if applicable.
        :type customer_id: Optional[str]
        :param reviews: A list of retrieved reviews.
        :type reviews: Optional[list[Review]]
        :param notes: Optional notes about the response.
        :type notes: Optional[str]
        :param errors: Optional error details.
        :type errors: Optional[str]
        """

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
    Response for moderating customer reviews.

    Attributes:
        status_code (int): The HTTP status code of the response.
        item_id (int): The ID of the item being reviewed.
        customer_id (str): The ID of the customer whose review is being moderated.
        new_flag (str): The new moderation status for the review.
        review (Optional[Review]): The updated review object, if moderation is successful.
        notes (Optional[str]): Additional notes related to the response.
        errors (Optional[str]): Error details, if any.
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
        """
        Initializes the ModerateReviewsResponse.

        Args:
            status_code (int): The HTTP status code of the response.
            item_id (int): The ID of the item being reviewed.
            customer_id (str): The ID of the customer whose review is being moderated.
            new_flag (str): The new moderation status for the review.
            review (Optional[Review], optional): The updated review object if successful. Defaults to None.
            notes (Optional[str], optional): Additional notes related to the response. Defaults to None.
            errors (Optional[str], optional): Error details if moderation fails. Defaults to None.

        Raises:
            ValueError: If the status code is unexpected or if required data is missing for a successful response.
            AssertionError: If the `review` object is missing when `status_code` indicates success.
        """

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

            assert review is not None, "You must provide reviews if status code is good"
            message = f"Moderate review successfully {identifier_message}. Changed it from {review.flagged} to {new_flag}"
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
