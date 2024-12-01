import os

from supabase import Client, create_client

from customer.schemas import Customer

url: str = "https://htwmmjekmptcxksqlaob.supabase.co"
key: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh0d21tamVrbXB0Y3hrc3FsYW9iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI5MDQ2ODksImV4cCI6MjA0ODQ4MDY4OX0.kfLUwS2Q5HNbEQJdhheXIxfBvm_HYYYkLdWiQV2DkjM"
)

supabase: Client = create_client(url, key)


def get_customer() -> Customer:
    return Customer(
        name="Hashem",
        username="hmk57",
        password="213123",
        age=12,
        address="123 Main Street",
        gender=False,
        marital_status="single",
        role="customer",
    )


def create_customer(customer: Customer):
    response = supabase.table("customer").insert(customer.model_dump()).execute()
    supabase.table("purchases").insert({})
    print(response)


response = create_customer(get_customer())
print(response)

response = supabase.table("customer").select("*").execute()
print(response)
