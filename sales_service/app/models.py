from typing import Optional

from pydantic import BaseModel, Field


class Purchase(BaseModel):
    """
    Represents a purchase made by a customer.

    Attributes:
        good_id (int): The ID of the good being purchased.
        customer_id (str): The ID of the customer making the purchase.
        amount_deducted (float): The amount deducted for the purchase. Must be non-negative.
        time (Optional[str]): The timestamp of when the purchase was made. Defaults to None.
    """

    good_id: int
    customer_id: str
    amount_deducted: float = Field(..., ge=0)
    time: Optional[str] = None
