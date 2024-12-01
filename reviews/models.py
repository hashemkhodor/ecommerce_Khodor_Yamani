import os

from dotenv import load_dotenv
from supabase import Client, create_client

from reviews.schemas import Review


class ReviewTable:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    def submit_review(self, review: Review) -> bool:
        print(review.model_dump(exclude={"time"}))
        content = (
            self.client.table("review")
            .insert(review.model_dump(exclude={"time"}))
            .execute()
        )
        if content.data:
            return True
        return False

    def get_all_reviews(self) -> list[Review]:
        content = self.client.table("review").select("*").execute()
        if content.data:
            return [Review.model_validate(**review) for review in content.data]
        return []

    def get_reviews_by_item_id(self, item_id: str) -> list[Review]:
        content = (
            self.client.table("review").select("*").eq("item_id", item_id).execute()
        )
        if content.data:
            return [Review.model_validate(**review) for review in content.data]
        return []

    def get_reviews_by_customer_id(self, customer_id: str) -> list[Review]:
        content = (
            self.client.table("review")
            .select("*")
            .eq("customer_id", customer_id)
            .execute()
        )
        if content.data:
            return [Review.model_validate(**review) for review in content.data]
        return []


if __name__ == "__main__":
    load_dotenv()
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")

    # supabase: Client = create_client(url, key)

    table: ReviewTable = ReviewTable(url=url, key=key)

    review = Review(
        customer_id="customer_id",
        item_id="3",
        rating=3,
        comment="comment",
        time=None,
        flagged="needs_approval",
    )
    print(table.submit_review(review))
    # print(table.get_all_reviews())
