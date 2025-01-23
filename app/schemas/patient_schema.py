from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class PatientStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class PatientBase(BaseModel):
    title: Literal["Mr.", "Mrs.", "Master"]
    first_name: str
    last_name: str
    phone: str
    emergency_contact: Optional[str] = None
    id_type: Literal["NIC", "Passport"]
    nic_passport: str
    email: EmailStr
    profile_picture_url: Optional[str] = None
    status: Optional[PatientStatus] = PatientStatus.ACTIVE

class PatientCreate(BaseModel):
    title: str
    first_name: str
    last_name: str
    phone: str
    emergency_contact: Optional[str] = None
    id_type: str
    nic_passport: str
    email: EmailStr
    profile_picture_url: Optional[str] = None
    status: str

class PatientUpdate(BaseModel):
    title: Optional[Literal["Mr.", "Mrs.", "Master"]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture_url: Optional[str] = None
    status: Optional[PatientStatus] = None

class PatientResponse(PatientBase):
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True