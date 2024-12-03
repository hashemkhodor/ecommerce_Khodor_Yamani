import os
from typing import List
from loguru import logger
from dotenv import load_dotenv
from app.models import Purchase
from supabase import Client, create_client
from postgrest import SyncRequestBuilder, SyncSelectRequestBuilder

class SalesTable:
    """
    Manages the sales (purchases) database table.

    Attributes:
        client (Client): The Supabase client for interacting with the database.
        table (SyncRequestBuilder): The purchases table for database queries.
    """

    def __init__(self, url: str, key: str):
        """
        Initializes the SalesTable with a Supabase client.

        :param url: The Supabase database URL.
        :type url: str
        :param key: The Supabase API key.
        :type key: str
        """

        self.client: Client = create_client(url, key)
        self.table: SyncRequestBuilder = self.client.table("purchases")

    def record_purchase(self, purchase: Purchase):
        """
        Records a new purchase in the database.

        :param purchase: The `Purchase` object containing purchase details.
        :type purchase: Purchase
        :return: The response data from the database after the record is inserted.
        :rtype: dict
        :raises Exception: If the purchase could not be recorded in the database.
        :notes: Logs the purchase details being added and any exceptions encountered.
        """

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
        """
        Retrieves all purchase records from the database.

        :return: A list of purchase records, or an empty list if no records are found.
        :rtype: List[dict]
        :raises Exception: If the database query fails.
        :notes: Logs any exceptions encountered during the database query.
        """

        response = self.client.table("purchases").select("*").execute()

        if not response.data:
            raise Exception(f"Failed to fetch purchases: {response.error.message}")
        return response.data or []  # return empty list if no records found
