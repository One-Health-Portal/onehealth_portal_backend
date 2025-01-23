# payment_schema.py
from pydantic import BaseModel, condecimal
from typing import Optional, Literal
from datetime import datetime

class PaymentBase(BaseModel):
    appointment_id: int
    amount: condecimal(max_digits=10, decimal_places=2) # type: ignore
    payment_date: datetime
    payment_status: Optional[Literal["Pending", "Completed", "Failed"]] = "Pending"

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    payment_status: Optional[Literal["Pending", "Completed", "Failed"]] = None
    payment_date: Optional[datetime] = None

class PaymentResponse(PaymentBase):
    payment_id: int

    class Config:
        from_attributes = True