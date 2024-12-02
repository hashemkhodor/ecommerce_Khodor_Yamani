from supabase import Client, create_client
from loguru import logger
from models import Good, GoodUpdate
from postgrest import SyncRequestBuilder, SyncSelectRequestBuilder

class InventoryTable:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.table: SyncRequestBuilder = self.client.table("inventory")

    def add_good_to_db(self, good: Good):
        good_data = good.model_dump()
        response = self.client.table("inventory").insert(good_data).execute()
        logger.info(f"Adding {good.model_dump()}")
        logger.info(response.data)

        if not response.data:
            raise Exception(f"Failed to add good: {response.error.message}")
        return response.data


    def update_good_in_db(self, good_id: int, updated_good: GoodUpdate):
        update_data = updated_good
        if not update_data:
            raise ValueError("No fields provided to update.")
        response = (
            self.client.table("inventory").update(update_data).eq("id", good_id).execute()
        )
        if not response.data:
            raise Exception(f"Failed to update good: {response.error.message}")
        return response.data


    def get_good_from_db(self, good_id: int):
        response = self.client.table("inventory").select("*").eq("id", good_id).execute()

        if not response.data:
            raise Exception(f"Failed to fetch good: {response.error.message}")
        return response.data[0]


    def deduct_good_from_db(self, good_id: int):
        # RPC the below to be defined in supabase
        """
        CREATE OR REPLACE FUNCTION deduct_inventory(good_id int)
        RETURNS void AS $$
        BEGIN
            UPDATE inventory
            SET count = count - 1
            WHERE id = good_id AND count > 0;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Stock is already zero or good not found!';
            END IF;
        END;
        $$ LANGUAGE plpgsql;
        """
        product = self.table.select("*").eq("id",good_id).execute()
        if product.data:
            product = product.data[0]
            product_count = product["count"]
            if(product_count>0):
                product_count = product_count-1
                response = (
                    self.client.table("inventory").update({"count":product_count}).eq("id", good_id).execute()
                )
            else:
                raise ValueError("Product count less than 0")

        if not response.data:
            raise Exception(f"Failed to deduct inventory: {response.error.message}")
        return response.data
