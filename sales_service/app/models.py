from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Purchase(BaseModel):
    good_id: int
    customer_id: str
    amount_deducted: float = Field(..., ge=0)
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
