import os
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from postgrest import SyncRequestBuilder, SyncSelectRequestBuilder
from starlette import status
from supabase import Client, create_client

from app.schemas import Review


class ReviewTable:
    """
    Handles database operations for managing reviews.

    Attributes:
        client (Client): The Supabase client for database operations.
        table (SyncRequestBuilder): The reviews table for database queries.
    """

    def __init__(self, url: str, key: str):
        """
        Initializes the ReviewTable with a Supabase client.

        :param url: The Supabase database URL.
        :type url: str
        :param key: The Supabase API key.
        :type key: str
        """

        self.client: Client = create_client(url, key)
        self.table: SyncRequestBuilder = self.client.table("review")

    def customer_and_item_exist(self, customer_id: str, item_id: int) -> int:
        """
        Verifies if the customer and item exist in the database.

        :param customer_id: The ID of the customer to check.
        :type customer_id: str
        :param item_id: The ID of the item to check.
        :type item_id: int
        :return: An HTTP status code indicating the existence or error.
        :rtype: int
        """

        try:
            if (
                not self.client.table("customer")
                .select("*")
                .eq("username", customer_id)
                .execute()
                .data
            ):
                return status.HTTP_400_BAD_REQUEST
            if (
                not self.client.table("inventory")
                .select("*")
                .eq("id", item_id)
                .execute()
                .data
            ):
                return status.HTTP_400_BAD_REQUEST

            return status.HTTP_200_OK
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            return status.HTTP_500_INTERNAL_SERVER_ERROR

    def submit_review(self, review: Review) -> Optional[list[Review]]:
        """
        Submits a new review to the database.

        :param review: The review object to submit.
        :type review: Review
        :return: A list containing the submitted review if successful, or None if an error occurs.
        :rtype: Optional[list[Review]]
        """

        try:
            logger.info(
                f"Verifying that item with id '{review.item_id}' and customer with id '{review.customer_id}' "
                f"exist"
            )

            logger.info(f"Submitting review: {review.model_dump()}")
            logger.info(review.model_dump(exclude={"time"}))
            content = self.table.insert(review.model_dump(exclude={"time"})).execute()

            if content.data:
                logger.success("Successfully submitted review")
                return [Review.model_validate(content.data[0])]
            logger.error("Failed to submit review")
            return []
        except Exception as e:
            logger.exception(e)
            return None

    def get_reviews(self, **filters) -> Optional[list[Review]]:
        """
        Retrieves reviews from the database based on filters.

        :param filters: Key-value pairs for filtering reviews (e.g., item_id=1).
        :return: A list of reviews that match the filters, or None if an error occurs.
        :rtype: Optional[list[Review]]
        """

        try:
            query: SyncSelectRequestBuilder = self.table.select("*")
            for _filter, value in filters.items():
                query = query.eq(_filter, value)

            logger.info(f"Fetching all reviews with filters: {filters}")
            content = query.execute()
            if content.data:
                logger.success("Successfully fetched the reviews")
                return [Review.model_validate(review) for review in content.data]
            logger.success("No reviews are available")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch reviews with filters: {filters}")
            logger.exception(e)
            return None

    def update_review(self, review: Review) -> Optional[list[Review]]:
        """
        Updates an existing review in the database.

        :param review: The updated review object.
        :type review: Review
        :return: A list containing the updated review, or None if an error occurs.
        :rtype: Optional[list[Review]]
        """

        try:
            logger.info(
                f"Updating review {review.item_id},{review.customer_id}: {review.model_dump()}"
            )
            query = (
                self.table.update(review.model_dump(exclude={"customer_id", "item_id"}))
                .eq("customer_id", review.customer_id)
                .eq("item_id", review.item_id)
                .execute()
            )
            if query.data:
                logger.success("Successfully updated the review")
                return [Review.model_validate(review) for review in query.data]
            logger.error("Failed to update the review")
            return []
        except Exception as e:
            logger.exception(e)
            return None

    def get_review(self, item_id: int, customer_id: str) -> Optional[list[Review]]:
        """
        Retrieves a specific review based on item and customer IDs.

        :param item_id: The ID of the item.
        :type item_id: int
        :param customer_id: The ID of the customer.
        :type customer_id: str
        :return: A list containing the matching review, or None if an error occurs.
        :rtype: Optional[list[Review]]
        """

        return self.get_reviews(item_id=item_id, customer_id=customer_id)

    def get_item_reviews(self, item_id: str) -> Optional[list[Review]]:
        """
        Retrieves all reviews for a specific item.

        :param item_id: The ID of the item to retrieve reviews for.
        :type item_id: str
        :return: A list of reviews for the item, or None if an error occurs.
        :rtype: Optional[list[Review]]
        """

        return self.get_reviews(item_id=item_id)

    def get_customer_reviews(self, customer_id: str) -> Optional[list[Review]]:
        """
        Retrieves all reviews submitted by a specific customer.

        :param customer_id: The ID of the customer to retrieve reviews for.
        :type customer_id: str
        :return: A list of reviews submitted by the customer, or None if an error occurs.
        :rtype: Optional[list[Review]]
        """

        return self.get_reviews(customer_id=customer_id)

    def delete_review(self, item_id: int, customer_id: str) -> Optional[bool]:
        """
        Deletes a review based on item and customer IDs.

        :param item_id: The ID of the item being reviewed.
        :type item_id: int
        :param customer_id: The ID of the customer who submitted the review.
        :type customer_id: str
        :return: True if the review was deleted successfully, False otherwise.
        :rtype: Optional[bool]
        """

        try:
            logger.info(f"Deleting {customer_id}'s review of item {item_id}")
            result = (
                self.table.delete()
                .eq("item_id", item_id)
                .eq("customer_id", customer_id)
                .execute()
            )
            if result.data:
                logger.success("Successfully delete the review")
                return True
            logger.error("Failed to delete the review")
            return False
        except Exception as e:
            logger.error(f"Failed to delete {customer_id}'s review of item {item_id}")
            logger.exception(e)


if __name__ == "__main__":
    load_dotenv()
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")

    # supabase: Client = create_client(url, key)

    table: ReviewTable = ReviewTable(url=url, key=key)

    review = Review(
        customer_id="user_id",
        item_id="3",
        rating=3,
        comment="comment",
        time=None,
        flagged="needs_approval",
    )
    print(table.submit_review(review))
    # print(table.get_all_reviews())
