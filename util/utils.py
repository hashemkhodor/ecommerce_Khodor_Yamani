import os
from random import choice, randint, uniform

from dotenv import load_dotenv
from faker import Faker

from customer.app.models import CustomerTable
from customer.app.schemas import Customer
from inventory_service.app.models import Good


def create_fake_customer() -> Customer:
    fake = Faker()
    return Customer(
        name=fake.name(),
        username=fake.user_name(),
        password=fake.password(),
        age=randint(18, 100),  # Age range: 18-100
        address=fake.address(),
        gender=choice([True, False]),
        marital_status=choice(["single", "married", "divorced", "widows"]),
        role=choice(["customer", "moderator", "admin"]),
    )


def generate_fake_goods(n: int = 10) -> list[Good]:
    fake = Faker()
    goods = []
    categories = ["food", "clothes", "accessories", "electronics"]

    for _ in range(n):
        goods.append(
            Good(
                name=fake.text(max_nb_chars=20).strip("."),
                category=choice(categories),
                price=round(uniform(1, 1000), 2),
                description=fake.text(max_nb_chars=50),
                count=randint(0, 100),
            )
        )

    return goods


if __name__ == "__main__":
    load_dotenv()
    customer_table: CustomerTable = CustomerTable(
        url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_KEY")
    )
    customers: list[Customer] = [create_fake_customer() for _ in range(10)]
    goods: list[Good] = generate_fake_goods(10)

    # _ = [customer_table.create_customer(customer) for customer in customers]
    _ = [
        customer_table.client.table("inventory").insert(good.model_dump()).execute()
        for good in goods
    ]

    print(create_fake_customer().model_dump())
    print(generate_fake_goods(10))
