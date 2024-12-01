import os
from typing import Optional

from dotenv import load_dotenv
from postgrest import SyncRequestBuilder, SyncSelectRequestBuilder
from supabase import Client, create_client
from loguru import logger
from reviews.schemas import Review


class ReviewTable:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.table: SyncRequestBuilder = self.client.table("review")

    def submit_review(self, review: Review) -> Optional[list[Review]]:
        try:
            logger.info(f"Submitting review: {review.model_dump()}")
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
        try:
            logger.info(f"Updating review {review.item_id},{review.customer_id}: {review.model_dump()}")
            query = self.table.update(review.model_dump(exclude={"customer_id", "item_id"}))\
                .eq("customer_id", review.customer_id).eq("item_id", review.item_id).execute()
            if query.data:
                logger.success("Successfully updated the review")
                return [Review.model_validate(review) for review in query.data]
            logger.error("Failed to update the review")
            return []
        except Exception as e:
            logger.exception(e)
            return None

    def get_review(self, item_id: int, customer_id: str) -> Optional[Review]:
        return self.get_reviews(item_id=item_id, customer_id=customer_id)

    def get_item_reviews(self, item_id: str) -> Optional[list[Review]]:
        return self.get_reviews(item_id=item_id)

    def get_customer_reviews(self, customer_id: str) -> Optional[list[Review]]:
        return self.get_reviews(customer_id=customer_id)

    def delete_review(self, item_id: int, customer_id: str) -> Optional[bool]:
        try:
            logger.info(f"Deleting {customer_id}'s review of item {item_id}")
            result = self.table.delete().eq("item_id", item_id).eq("customer_id", customer_id).execute()
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
