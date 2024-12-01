import random

from faker import Faker

from customer.schemas import Customer


def create_fake_customer() -> Customer:
    fake = Faker()
    return Customer(
        name=fake.name(),
        username=fake.user_name(),
        password=fake.password(),
        age=random.randint(18, 100),  # Age range: 18-100
        address=fake.address(),
        gender=random.choice([True, False]),
        marital_status=random.choice(["single", "married", "divorced", "widows"]),
        role=random.choice(["customer", "moderator", "admin"]),
    )


if __name__ == "__main__":
    print(create_fake_customer().model_dump())
