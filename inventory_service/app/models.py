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

    :param name: The name of the item (maximum length: 100 characters).
    :type name: str
    :param category: The category of the item. Must be one of ['food', 'clothes', 'accessories', 'electronics'].
    :type category: Literal["food", "clothes", "accessories", "electronics"]
    :param price: The price of the item. Must be greater than 0.
    :type price: float
    :param description: A brief description of the item (maximum length: 255 characters).
    :type description: str
    :param count: The number of items available in stock. Must be non-negative.
    :type count: int
    """

    name: str = Field(..., max_length=100)
    category: Literal["food", "clothes", "accessories", "electronics"]
    price: float = Field(..., gt=0)
    description: str = Field(..., max_length=255)
    count: int = Field(..., ge=0)


class GoodUpdate(BaseModel):
    """
    Represents the fields for updating an inventory item.

    :param name: The new name of the item (maximum length: 100 characters). Optional.
    :type name: Optional[str]
    :param category: The new category of the item. Must be one of ['food', 'clothes', 'accessories', 'electronics']. Optional.
    :type category: Optional[Category]
    :param price: The new price of the item. Must be greater than 0. Optional.
    :type price: Optional[float]
    :param description: The new description of the item (maximum length: 255 characters). Optional.
    :type description: Optional[str]
    :param count: The new stock count of the item. Must be non-negative. Optional.
    :type count: Optional[int]
    """

    name: Optional[str] = Field(None, max_length=100)
    category: Optional[Category] = None
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)
    count: Optional[int] = Field(None, ge=0)
