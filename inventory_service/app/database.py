from app.models import Good, GoodUpdate
from loguru import logger
from postgrest import SyncRequestBuilder, SyncSelectRequestBuilder
from supabase import Client, create_client


class InventoryTable:
    """
    Manages the inventory database table.

    :param url: The Supabase database URL.
    :type url: str
    :param key: The Supabase API key.
    :type key: str

    :ivar client: The Supabase client for database operations.
    :vartype client: Client
    :ivar table: The inventory table for database queries.
    :vartype table: SyncRequestBuilder
    """

    def __init__(self, url: str, key: str):
        """
        Initializes the InventoryTable with a Supabase client.

        :param url: The Supabase database URL.
        :type url: str
        :param key: The Supabase API key.
        :type key: str
        """

        self.client: Client = create_client(url, key)
        self.table: SyncRequestBuilder = self.client.table("inventory")

    def add_good_to_db(self, good: Good):
        """
        Adds a new inventory item to the database.

        :param good: The `Good` object containing the item details.
        :type good: Good
        :return: The response data from the database after insertion.
        :rtype: dict
        :raises Exception: If the item could not be added to the database.
        """

        good_data = good.model_dump()
        response = self.client.table("inventory").insert(good_data).execute()
        logger.info(f"Adding {good.model_dump()}")
        logger.info(response.data)

        if not response.data:
            raise Exception(f"Failed to add good: {response.error.message}")
        return response.data

    def update_good_in_db(self, good_id: int, updated_good: GoodUpdate):
        """
        Updates an existing inventory item in the database.

        :param good_id: The ID of the item to update.
        :type good_id: int
        :param updated_good: The fields to update as a `GoodUpdate` object.
        :type updated_good: GoodUpdate
        :return: The response data from the database after the update.
        :rtype: dict
        :raises ValueError: If no fields are provided for the update.
        :raises Exception: If the item could not be updated in the database.
        """

        update_data = updated_good
        if not update_data:
            raise ValueError("No fields provided to update.")
        response = (
            self.client.table("inventory")
            .update(update_data)
            .eq("id", good_id)
            .execute()
        )
        if not response.data:
            raise Exception(f"Failed to update good: {response.error.message}")
        return response.data

    def get_good_from_db(self, good_id: int):
        """
        Retrieves an inventory item by its ID.

        :param good_id: The ID of the item to retrieve.
        :type good_id: int
        :return: The details of the retrieved item.
        :rtype: dict
        :raises Exception: If the item could not be fetched from the database.
        """

        response = (
            self.client.table("inventory").select("*").eq("id", good_id).execute()
        )

        if not response.data:
            raise Exception(f"Failed to fetch good: {response.error.message}")
        return response.data[0]

    def deduct_good_from_db(self, good_id: int):
        """
        Deducts one unit from the stock of an inventory item by its ID.

        :param good_id: The ID of the item to deduct.
        :type good_id: int
        :return: The response data from the database after deduction.
        :rtype: dict
        :raises ValueError: If the item stock is already zero.
        :raises Exception: If the inventory update fails.
        """
        product = self.table.select("*").eq("id", good_id).execute()
        if product.data:
            product = product.data[0]
            product_count = product["count"]
            if product_count > 0:
                product_count = product_count - 1
                response = (
                    self.client.table("inventory")
                    .update({"count": product_count})
                    .eq("id", good_id)
                    .execute()
                )
            else:
                raise ValueError("Product count less than 0")

        if not response.data:
            raise Exception(f"Failed to deduct inventory: {response.error.message}")
        return response.data
