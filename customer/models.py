import os
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from postgrest import SyncRequestBuilder
from supabase import Client, create_client

from customer.schemas import Customer, Wallet


class CustomerTable:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)
        self.table: SyncRequestBuilder = self.client.table("customer")

    def create_customer(self, customer: Customer) -> Optional[bool]:
        try:
            logger.info(f"Creating customer {customer.model_dump()}")

            content = self.table.insert(customer.model_dump()).execute()
            if content.data:
                logger.info("Successfully created customer")
                # create wallet
                logger.info(f"Creating wallet for customer {customer.username}")
                wallet = (
                    self.client.table("wallet")
                    .insert({"customer_id": customer.username, "amount": 0.0})
                    .execute()
                )
                if wallet.data:
                    logger.info("Successfully created wallet")
                    return True
                logger.error("Could not create wallet")
                return False

            logger.error("Failed creating customer")
            return False
        except Exception as e:
            logger.exception(e)
            return None

    def get_users(self, **filters) -> Optional[list[Customer]]:
        try:
            query = self.table.select("*")
            for _filter, value in filters.items():
                query = query.eq(_filter, value)
            content = query.execute()
            if content.data:
                logger.info(
                    f"Successfully retrieved users with the following filters {filters}"
                )
                return [Customer.model_validate(customer) for customer in content.data]
            logger.info("No users found")
            return []
        except Exception as e:
            logger.exception(e)
            return None

    def get_customers(self) -> Optional[list[Customer]]:
        return self.get_users(role="customer")

    def get_user(self, user_id: str) -> Optional[list[Customer]]:
        result: Optional[list[dict]] = self.get_users(username=user_id)
        if result is None:
            return result
        elif result:
            return [Customer.model_validate(result[0])]
        return []

    def get_wallet(self, user_id: str) -> Optional[list[Wallet]]:
        try:
            result = (
                self.client.table("wallet")
                .select("*")
                .eq("customer_id", user_id)
                .execute()
            )
            if result.data is None:
                return []
            return [Wallet.model_validate(result.data[0])]

        except Exception as e:
            logger.exception(e)
            return None

    def update_wallet(self, user_id: str, amount: float) -> Optional[list[Wallet]]:
        try:
            wallet = self.get_wallet(user_id)
            if not wallet:
                return wallet

            updated_wallet = (
                self.client.table("wallet")
                .update({"amount": wallet[0].amount + amount})
                .eq("customer_id", user_id)
                .execute()
            )

            if updated_wallet.data:
                return [Wallet.model_validate(updated_wallet.data[0])]

            return []
        except Exception as e:
            logger.exception(e)
            return None

    def deduct_wallet(self, user_id: str, amount: float) -> Optional[list[Wallet]]:
        assert isinstance(amount, float) and amount < 0, "Amount must be less than 0"

        return self.update_wallet(user_id, amount)

    def charge_wallet(self, user_id: str, amount: float) -> Optional[list[Wallet]]:
        assert (
            isinstance(amount, float) and amount >= 0
        ), "Amount must be greater than or equal 0"

        return self.update_wallet(user_id, amount)

    def delete_user(self, user_id: str) -> bool:
        try:
            if self.get_users(username=user_id) is None:
                logger.info(f"User with username {user_id} not found")
                return False

            self.table.delete().eq("username", user_id).execute()
            self.client.table("wallet").delete().eq("customer_id", user_id).execute()

            logger.info(f"Deleted user with username {user_id}")
            return True

        except Exception as e:
            logger.exception(e)
            return False

    def update_user(
        self, user_id: str, new_customer: Customer
    ) -> Optional[list[Customer]]:
        if self.get_users(username=user_id) is None:
            logger.info(f"User with username {user_id} not found")
            return []
        result = (
            self.table.update(new_customer.model_dump(exclude={"username"}))
            .eq("username", new_customer.username)
            .execute()
        )
        if result.data:
            return [Customer.model_validate(result.data[0])]
        return None


if __name__ == "__main__":
    load_dotenv()
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")

    # supabase: Client = create_client(url, key)

    table: CustomerTable = CustomerTable(url=url, key=key)
    customer_dict: dict = {
        "name": "David Weiss",
        "username": "collierjared",
        "password": "9(5KZl8%&R",
        "age": 79,
        "address": "230 Cindy Crescent\nEvanburgh, MA 98005",
        "gender": False,
        "marital_status": "single",
        "role": "customer",
    }
    customer: Customer = Customer(**customer_dict)

    # print(table.create_customer(customer=customer))
    # print(table.get_customers())
    print(table.get_user(user_id="hmk57"))
    print(table.get_user(user_id="hmk5237"))

    print(table.get_users(name="David Weiss"))

    print(
        table.update_user(
            user_id="collierjared",
            new_customer=Customer(**{**customer_dict, "name": "HASHOUNMA"}),
        )
    )
    print(table.get_user(user_id="collierjared"))
