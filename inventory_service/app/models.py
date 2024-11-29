from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Category(str, Enum):
    FOOD = "food"
    CLOTHES = "clothes"
    ACCESSORIES = "accessories"
    ELECTRONICS = "electronics"

class Good(BaseModel):
    name: str = Field(..., max_length=100)
    category: Category
    price: float = Field(..., gt=0)
    description: str = Field(..., max_length=255)
    count: int = Field(..., ge=0)

class GoodUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[Category] = None
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)
    count: Optional[int] = Field(None, ge=0)
