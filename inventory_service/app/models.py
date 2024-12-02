from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    FOOD = "food"
    CLOTHES = "clothes"
    ACCESSORIES = "accessories"
    ELECTRONICS = "electronics"


class Good(BaseModel):
    name: str = Field(..., max_length=100)
    category: Literal["food", "clothes", "accessories", "electronics"]
    price: float = Field(..., gt=0)
    description: str = Field(..., max_length=255)
    count: int = Field(..., ge=0)


class GoodUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[Category] = None
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)
    count: Optional[int] = Field(None, ge=0)
