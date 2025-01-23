# hospital_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HospitalBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_services_available: bool = False
    logo_url: Optional[str] = None

class HospitalCreate(HospitalBase):
    pass

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_services_available: Optional[bool] = None
    logo_url: Optional[str] = None

class HospitalResponse(HospitalBase):
    hospital_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True