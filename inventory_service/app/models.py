from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    FOOD = "food"
    CLOTHES = "clothes"
    ACCESSORIES = "accessories"
    ELECTRONICS = "electronics"


class Good(BaseModel):
    """
    Represents an inventory item.

    Attributes:
        name (str): The name of the item (maximum length: 100 characters).
        category (Literal["food", "clothes", "accessories", "electronics"]): The category of the item.
        price (float): The price of the item. Must be greater than 0.
        description (str): A brief description of the item (maximum length: 255 characters).
        count (int): The number of items available in stock. Must be non-negative.
    """

    name: str = Field(..., max_length=100)
    category: Literal["food", "clothes", "accessories", "electronics"]
    price: float = Field(..., gt=0)
    description: str = Field(..., max_length=255)
    count: int = Field(..., ge=0)


class GoodUpdate(BaseModel):
    """
    Represents the fields for updating an inventory item.

    Attributes:
        name (Optional[str]): The new name of the item (maximum length: 100 characters).
        category (Optional[Category]): The new category of the item.
        price (Optional[float]): The new price of the item. Must be greater than 0.
        description (Optional[str]): The new description of the item (maximum length: 255 characters).
        count (Optional[int]): The new stock count of the item. Must be non-negative.
    """

    name: Optional[str] = Field(None, max_length=100)
    category: Optional[Category] = None
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)
    count: Optional[int] = Field(None, ge=0)
