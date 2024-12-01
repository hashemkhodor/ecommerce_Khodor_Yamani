from supabase import create_client, Client
from typing import List
from models import Purchase

url: str = "abc"
key: str = "bdhhi"

supabase: Client = create_client(url, key)

def record_purchase(purchase: Purchase):
    response = supabase.table("purchases").insert(purchase.dict()).execute()

    if response.error:
        raise Exception(f"Failed to record purchase: {response.error.message}")
    return response.data

def get_purchases() -> List[dict]:
    response = supabase.table("purchases").select("*").execute()

    if response.error:
        raise Exception(f"Failed to fetch purchases: {response.error.message}")
    return response.data or []  # return empty list if no records found
