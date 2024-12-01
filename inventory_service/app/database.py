from supabase import create_client, Client
from customer.schemas import Customer
from models import Good, GoodUpdate

url: str = "dehdwgu"
key: str = "dehuehuiuh"

supabase: Client = create_client(url, key)

def add_good_to_db(good: Good):
    good_data = good.model_dump()
    response = supabase.table("inventory").insert(good_data).execute()
    if response.error:
        raise Exception(f"Failed to add good: {response.error.message}")
    return response.data

def update_good_in_db(good_id: int, updated_good: GoodUpdate):
    update_data = updated_good.model_dump(exclude_none=True)
    if not update_data:
        raise ValueError("No fields provided to update.")
    response = supabase.table("inventory").update(update_data).eq("id", good_id).execute()
    if response.error:
        raise Exception(f"Failed to update good: {response.error.message}")
    return response.data

def get_good_from_db(good_id: int):
    response = supabase.table("inventory").select("*").eq("id", good_id).execute()

    if response.error:
        raise Exception(f"Failed to fetch good: {response.error.message}")
    if not response.data:
        raise ValueError(f"Good with id {good_id} not found")
    return response.data[0]


def deduct_good_from_db(good_id: int):
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
    response = supabase.rpc("deduct_inventory", {"good_id": good_id}).execute()

    if response.error:
        raise Exception(f"Failed to deduct inventory: {response.error.message}")
    return response.data