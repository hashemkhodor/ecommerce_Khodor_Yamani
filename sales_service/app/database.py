import os
from typing import List

from app.models import Purchase
from dotenv import load_dotenv
from loguru import logger
from postgrest import SyncRequestBuilder, SyncSelectRequestBuilder
from supabase import Client, create_client


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
            response = self.table.insert(
                purchase.model_dump(exclude={"time"})
            ).execute()
            logger.info(response)

            if not response.data:
                error_message = (
                    response.error.message if response.error else "Unknown error"
                )
                raise Exception(f"Failed to record purchase: {error_message}")
            return response.data
        except Exception as e:
            logger.exception(e)
            raise

    def get_purchases(self) -> List[dict]:
        """
        Retrieves all purchase records from the database.

        :return: A list of purchase records, or an empty list if no records are found.
        :rtype: List[dict]
        :raises Exception: If the database query fails.
        :notes: Logs any exceptions encountered during the database query.
        """

        try:
            response = self.table.select("*").execute()

            if not response:

                raise Exception(f"Failed to fetch purchases")
            return response.data or []  # return empty list if no records found
        except Exception as e:
            logger.exception(e)
            raise  # Re-raise the exception
