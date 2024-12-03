from typing import Optional

from pydantic import BaseModel, Field


class Purchase(BaseModel):
    good_id: int
    customer_id: str
    amount_deducted: float = Field(..., ge=0)
    time: Optional[str] = None
