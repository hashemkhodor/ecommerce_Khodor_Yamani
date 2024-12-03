import os
from typing import List
from loguru import logger
from dotenv import load_dotenv
from app.models import Purchase
from supabase import Client, create_client
from postgrest import SyncRequestBuilder, SyncSelectRequestBuilder

class SalesTable:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.table: SyncRequestBuilder = self.client.table("purchases")

    def record_purchase(self, purchase: Purchase):
        logger.info(f"Adding {purchase.model_dump()}")
        try:
            response = self.client.table("purchases").insert(purchase.model_dump(exclude={'time'})).execute()
            logger.info(response)

            if not response.data:
                raise Exception(f"Failed to record purchase: {response.error.message}")
            return response.data
        except Exception as e:
            logger.exception(e)


    def get_purchases(self) -> List[dict]:
        response = self.client.table("purchases").select("*").execute()

        if not response.data:
            raise Exception(f"Failed to fetch purchases: {response.error.message}")
        return response.data or []  # return empty list if no records found
