from typing import List

from models import Purchase
from supabase import Client, create_client
from dotenv import load_dotenv
import os

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# Ensure they are properly loaded
if not url or not key:
    raise ValueError("Supabase URL or key not found. Check your .env file.")

supabase: Client = create_client(url, key)


def record_purchase(purchase: Purchase):
    response = supabase.table("purchases").insert(purchase.model_dump()).execute()

    if response.error:
        raise Exception(f"Failed to record purchase: {response.error.message}")
    return response.data


def get_purchases() -> List[dict]:
    response = supabase.table("purchases").select("*").execute()

    if response.error:
        raise Exception(f"Failed to fetch purchases: {response.error.message}")
    return response.data or []  # return empty list if no records found
